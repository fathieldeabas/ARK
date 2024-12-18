from django.core.mail import EmailMultiAlternatives
from django.conf import settings



from django.core.paginator import Paginator
import xlwt
from celery import Task
from django.utils.translation import gettext as _
from django.urls import reverse
import random
import string
from .models import Allocation
from django.db.models import Sum
from project.models import Project


def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def deliver_mail(subject,message_body, recipients=None):
    """
    Send a message to inform the user with disbursement/collection related action.
    :param user_obj: Request's user instance that the mail will be sent to.
    :param subject_tail: Tailed mail subject header after his/her chosen mail header brand.
    :param message_body: Body of the message that will be sent.
    :param recipients: If there are multiple makers/checkers to be notified.
    :return: Action of sending the mail to the user.
    """
    from_email = settings.SERVER_EMAIL

    subject = subject
    recipient_list = ["manager.com"]

    message_body=message_body
    mail_to_be_sent = EmailMultiAlternatives(
        subject, message_body, from_email, recipient_list
    )
    mail_to_be_sent.attach_alternative(message_body, "text/html")
    mail_to_be_sent.send()
    return


class Export_Employee_allocation_percentages(Task):

    def create_report(self):
        filename = f"Employee_allocation_percentages_{randomword(8)}.xls"
        file_path = f"{settings.MEDIA_ROOT}/documents/{filename}"
        wb = xlwt.Workbook(encoding='utf-8')

        paginator = Paginator(self.data, 65535)
        for page_number in paginator.page_range:
            queryset = paginator.page(page_number)
            column_names_list = [
                "employee",
                "project",
                "allocation_percentage"
            ]
            ws = wb.add_sheet(f'page{page_number}', cell_overwrite_ok=True)

            # 1. Write sheet header/column names - first row
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True

            for col_nums in range(len(column_names_list)):
                ws.write(row_num, col_nums, column_names_list[col_nums], font_style)

            row_num = row_num + 1

            for row in queryset:
                ws.write(row_num, 0, str(row.employee))
                ws.write(row_num, 1, str(row.project))
                ws.write(row_num, 2, str(row.allocation_percentage))

                row_num = row_num + 1

        wb.save(file_path)

        # add new file for this user in ExcelFile model

        report_download_url = f"{settings.BASE_URL}{str(reverse('allocation:download_exported'))}?filename={filename}"
        return report_download_url

    def run(self):
        self.data= Allocation.objects.all()

        download_url = self.create_report()
        mail_content = _(
            f"You can download "
            f"from here <a href='{download_url}' >Download</a>.<br><br>Best Regards,"
        )
        mail_subject = " Employee allocation percentages Report"
        deliver_mail( _(mail_subject), mail_content)




class Notify_managers_total_allocation_percentage(Task):

    def run(self):
        data={}
        allocation_sum_per_employee = Allocation.objects.values('employee') \
    .annotate(total_allocation_percentage=Sum('allocation_percentage')) \
    .order_by('employee')
        for allocation in allocation_sum_per_employee:
            if allocation['total_allocation_percentage'] > 100:
                data[allocation['employee']] = allocation['total_allocation_percentage']
        mail_content = _(
            f"Dears, Kindly note these employee {data} allocation exceeds 100%</a>.<br><br>Best Regards,"
        )
        mail_subject = " Employee allocation percentages Report"
        deliver_mail( _(mail_subject), mail_content)


class Notify_managers_project_capacity_exceeded(Task):
    def run(self):
        data={}
        projects=Project.objects.all()
        for project in projects:
            if project.capacity < project.Allocation:
                data[project.name] = project.Allocation
                
        mail_content = _(
            f"Dears, Kindly note these projects {data} exceeds</a>.<br><br>Best Regards,"
        )
        mail_subject = "project's capacity is exceeded"
        deliver_mail( _(mail_subject), mail_content)
