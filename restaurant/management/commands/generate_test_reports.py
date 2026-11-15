from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from restaurant.reporting import generate_all_reports


class Command(BaseCommand):
    help = 'Run every automated test suite and create Excel workbooks for each along with the Testing Topics Guide.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=Path,
            default=Path(settings.BASE_DIR) / 'test_reports',
            help='Directory for generated Excel workbooks (defaults to the project test_reports directory).',
        )

    def handle(self, *args, **options):
        reports_dir = options['output_dir']
        reports_dir.mkdir(parents=True, exist_ok=True)

        def on_event(event):
            msg = event.get('message')
            if msg:
                if event.get('type') == 'test_record':
                    self.stdout.write(self.style.SUCCESS(msg))
                elif event.get('type') in ('suite_start', 'report_gen_start'):
                    self.stdout.write(self.style.WARNING(msg))
                else:
                    self.stdout.write(msg)

        summary = generate_all_reports(output_dir=reports_dir, progress_callback=on_event)

        if not summary['success']:
            raise CommandError(
                f"Test failures in: {', '.join(summary['failed_suites'])}. Reports were still generated."
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"All {summary['total_suites']} test suites ({summary['total_tests']} tests) passed and Excel reports were generated in {reports_dir}."
            )
        )
