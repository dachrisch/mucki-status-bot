# coding=utf-8
from service.action import CommandActionMixin


class InvoiceCommandAction(CommandActionMixin):
    @property
    def help_text(self):
        return 'Display invoicing options'

    @property
    def name(self):
        return 'invoices'

    def _writer_callback(self, writer, message=None):
        writer.out('https://invoicing-suedsterne.e4ff.pro-eu-west-1.openshiftapps.com/')
