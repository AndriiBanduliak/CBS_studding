"""
Management command to clean up old transcriptions, conversations, and syntheses.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from asr.models import Transcription
from llm.models import Conversation
from tts.models import Synthesis
import logging

logger = logging.getLogger('core')


class Command(BaseCommand):
    help = 'Clean up old transcriptions, conversations, and syntheses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Delete records older than this many days (default: 90)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        cutoff_date = timezone.now() - timedelta(days=days)

        self.stdout.write(f"Cleaning up records older than {days} days (before {cutoff_date})")

        # Clean up transcriptions
        transcriptions = Transcription.objects.filter(created_at__lt=cutoff_date)
        trans_count = transcriptions.count()
        if dry_run:
            self.stdout.write(f"Would delete {trans_count} transcriptions")
        else:
            # Delete associated files first
            for trans in transcriptions:
                try:
                    if trans.audio_file:
                        trans.audio_file.delete(save=False)
                except Exception as e:
                    logger.warning(f"Failed to delete audio file for transcription {trans.id}: {e}")
            deleted = transcriptions.delete()[0]
            self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} transcriptions"))

        # Clean up conversations (only empty or very old)
        conversations = Conversation.objects.filter(
            created_at__lt=cutoff_date,
            messages__isnull=True
        ).distinct()
        conv_count = conversations.count()
        if dry_run:
            self.stdout.write(f"Would delete {conv_count} empty conversations")
        else:
            deleted = conversations.delete()[0]
            self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} conversations"))

        # Clean up syntheses
        syntheses = Synthesis.objects.filter(created_at__lt=cutoff_date)
        synth_count = syntheses.count()
        if dry_run:
            self.stdout.write(f"Would delete {synth_count} syntheses")
        else:
            # Delete associated files first
            for synth in syntheses:
                try:
                    if synth.audio_file:
                        synth.audio_file.delete(save=False)
                except Exception as e:
                    logger.warning(f"Failed to delete audio file for synthesis {synth.id}: {e}")
            deleted = syntheses.delete()[0]
            self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} syntheses"))

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run completed. Use without --dry-run to actually delete."))
        else:
            self.stdout.write(self.style.SUCCESS("Cleanup completed successfully!"))

