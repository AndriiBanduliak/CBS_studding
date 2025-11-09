"""
Management command to export user data.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from asr.models import Transcription
from llm.models import Conversation, Message
from tts.models import Synthesis
import json
import csv
from pathlib import Path
from datetime import datetime

User = get_user_model()


class Command(BaseCommand):
    help = 'Export user data to JSON'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username to export data for',
        )
        parser.add_argument(
            '--output',
            type=str,
            default='export',
            help='Output directory (default: export)',
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['json', 'csv', 'both'],
            default='json',
            help='Export format: json, csv, or both (default: json)',
        )

    def handle(self, *args, **options):
        username = options['username']
        output_dir = Path(options['output'])
        output_dir.mkdir(exist_ok=True)

        export_format = options['format']
        
        if username:
            try:
                user = User.objects.get(username=username)
                self.export_user_data(user, output_dir, export_format)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"User '{username}' not found"))
        else:
            # Export all users
            for user in User.objects.all():
                self.export_user_data(user, output_dir, export_format)

        self.stdout.write(self.style.SUCCESS(f"Export completed to {output_dir}"))

    def export_user_data(self, user, output_dir, export_format='json'):
        """Export data for a single user."""
        user_dir = Path(output_dir) / user.username
        user_dir.mkdir(parents=True, exist_ok=True)

        # Export transcriptions
        transcriptions = Transcription.objects.filter(user=user)
        trans_data = []
        for trans in transcriptions:
            trans_data.append({
                'id': trans.id,
                'text': trans.text,
                'language': trans.language,
                'created_at': trans.created_at.isoformat(),
            })
        
        # Export transcriptions
        if export_format in ['json', 'both']:
            with open(user_dir / 'transcriptions.json', 'w', encoding='utf-8') as f:
                json.dump(trans_data, f, indent=2, ensure_ascii=False)
        
        if export_format in ['csv', 'both']:
            if trans_data:
                with open(user_dir / 'transcriptions.csv', 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['id', 'text', 'language', 'created_at'])
                    writer.writeheader()
                    writer.writerows(trans_data)

        # Export conversations
        conversations = Conversation.objects.filter(user=user).prefetch_related('messages')
        conv_data = []
        for conv in conversations:
            messages = []
            for msg in conv.messages.all():
                messages.append({
                    'role': msg.role,
                    'content': msg.content,
                    'created_at': msg.created_at.isoformat(),
                })
            conv_data.append({
                'id': conv.id,
                'title': conv.title,
                'messages': messages,
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat(),
            })
        
        # Export conversations
        if export_format in ['json', 'both']:
            with open(user_dir / 'conversations.json', 'w', encoding='utf-8') as f:
                json.dump(conv_data, f, indent=2, ensure_ascii=False)
        
        if export_format in ['csv', 'both']:
            if conv_data:
                # Flatten conversations for CSV
                csv_data = []
                for conv in conv_data:
                    csv_data.append({
                        'id': conv['id'],
                        'title': conv['title'],
                        'message_count': len(conv['messages']),
                        'created_at': conv['created_at'],
                        'updated_at': conv['updated_at'],
                    })
                with open(user_dir / 'conversations.csv', 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['id', 'title', 'message_count', 'created_at', 'updated_at'])
                    writer.writeheader()
                    writer.writerows(csv_data)

        # Export syntheses
        syntheses = Synthesis.objects.filter(user=user)
        synth_data = []
        for synth in syntheses:
            synth_data.append({
                'id': synth.id,
                'text': synth.text,
                'voice': synth.voice,
                'created_at': synth.created_at.isoformat(),
            })
        
        # Export syntheses
        if export_format in ['json', 'both']:
            with open(user_dir / 'syntheses.json', 'w', encoding='utf-8') as f:
                json.dump(synth_data, f, indent=2, ensure_ascii=False)
        
        if export_format in ['csv', 'both']:
            if synth_data:
                with open(user_dir / 'syntheses.csv', 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['id', 'text', 'voice', 'created_at'])
                    writer.writeheader()
                    writer.writerows(synth_data)

        self.stdout.write(f"Exported data for user: {user.username} (format: {export_format})")

