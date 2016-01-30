from openerp import tools
from openerp.osv import fields, osv

class account_invoice_report(osv.osv):
    _inherit = 'account.invoice.report'
    _columns = {
                 
         'profit_total': fields.float('Total Profit', readonly=True),
        }
    
    def create(self, vals):
        res = super(account_invoice_report,self).create(vals)
        pp = self.env['product.product'].browse(vals['product_id'])
        std_price = pp.total_cost_all
        vals['cost_total'] = std_price
        return res
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'account_invoice_report')
        cr.execute("""
        CREATE OR REPLACE VIEW account_invoice_report AS 
         WITH currency_rate(currency_id, rate, date_start, date_end) AS (
         SELECT r.currency_id,
            r.rate,
            r.name AS date_start,
            ( SELECT r2.name
                   FROM res_currency_rate r2
                  WHERE r2.name > r.name AND r2.currency_id = r.currency_id
                  ORDER BY r2.name
                 LIMIT 1) AS date_end
           FROM res_currency_rate r
        )
 SELECT sub.id,
    sub.date,
    sub.product_id,
    sub.partner_id,
    sub.country_id,
    sub.payment_term,
    sub.period_id,
    sub.uom_name,
    sub.currency_id,
    sub.journal_id,
    sub.fiscal_position,
    sub.user_id,
    sub.company_id,
    sub.nbr,
    sub.type,
    sub.state,
    sub.categ_id,
    sub.date_due,
    sub.account_id,
    sub.account_line_id,
    sub.partner_bank_id,
    sub.product_qty,
    sub.profit_total,
    sub.price_total / cr.rate AS price_total,
    sub.price_average / cr.rate AS price_average,
    cr.rate AS currency_rate,
    sub.residual / cr.rate AS residual,
    sub.commercial_partner_id,
    sub.section_id
   FROM ( SELECT min(ail.id) AS id,
            ai.date_invoice AS date,
            ail.product_id,
            ai.partner_id,
            ai.payment_term,
            ai.period_id,
            u2.name AS uom_name,
            ai.currency_id,
            ai.journal_id,
            ai.fiscal_position,
            ai.user_id,
            ai.company_id,
            count(ail.*) AS nbr,
            ai.type,
            ai.state,
            pt.categ_id,
            ai.date_due,
            ai.account_id,
            ail.account_id AS account_line_id,
            ai.partner_bank_id,
            sum(
                CASE
                    WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text]) THEN (- ail.quantity) / u.factor * u2.factor
                    ELSE ail.quantity / u.factor * u2.factor
                END) AS product_qty,
            sum(
                CASE
                    WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text]) THEN - ail.price_subtotal - ((ail.quantity / u.factor * u2.factor))
                    ELSE ail.price_subtotal - ((ail.quantity / u.factor * u2.factor))
                END) AS profit_total,
            sum(
                CASE
                    WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text]) THEN - ail.price_subtotal
                    ELSE ail.price_subtotal
                END) AS price_total,
                CASE
                    WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text]) THEN sum(- ail.price_subtotal)
                    ELSE sum(ail.price_subtotal)
                END /
                CASE
                    WHEN sum(ail.quantity / u.factor * u2.factor) <> 0::numeric THEN
                    CASE
                        WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text]) THEN sum((- ail.quantity) / u.factor * u2.factor)
                        ELSE sum(ail.quantity / u.factor * u2.factor)
                    END
                    ELSE 1::numeric
                END AS price_average,
                CASE
                    WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text]) THEN - ai.residual
                    ELSE ai.residual
                END / (( SELECT count(*) AS count
                   FROM account_invoice_line l
                  WHERE l.invoice_id = ai.id))::numeric * count(*)::numeric AS residual,
            ai.commercial_partner_id,
            partner.country_id,
            ai.section_id
           FROM account_invoice_line ail
             JOIN account_invoice ai ON ai.id = ail.invoice_id
             JOIN res_partner partner ON ai.commercial_partner_id = partner.id
             LEFT JOIN product_product pr ON pr.id = ail.product_id
             LEFT JOIN product_template pt ON pt.id = pr.product_tmpl_id
             LEFT JOIN product_uom u ON u.id = ail.uos_id
             LEFT JOIN product_uom u2 ON u2.id = pt.uom_id
          GROUP BY ail.product_id, ai.date_invoice, ai.id, ai.partner_id, ai.payment_term, ai.period_id, u2.name, u2.id, ai.currency_id, ai.journal_id, ai.fiscal_position, ai.user_id, ai.company_id, ai.type, ai.state, pt.categ_id, ai.date_due, ai.account_id, ail.account_id, ai.partner_bank_id, ai.residual, ai.amount_total, ai.commercial_partner_id, partner.country_id, ai.section_id) sub
     JOIN currency_rate cr ON cr.currency_id = sub.currency_id AND cr.date_start <= COALESCE(sub.date::timestamp with time zone, now()) AND (cr.date_end IS NULL OR cr.date_end > COALESCE(sub.date::timestamp with time zone, now()));

ALTER TABLE account_invoice_report
  OWNER TO odoo;
        """)
account_invoice_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
