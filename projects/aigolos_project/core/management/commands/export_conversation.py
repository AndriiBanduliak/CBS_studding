"""
Management command to export conversation to PDF or Markdown.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from llm.models import Conversation, Message
from pathlib import Path
import json

User = get_user_model()


class Command(BaseCommand):
    help = 'Export conversation to PDF or Markdown'

    def add_arguments(self, parser):
        parser.add_argument(
            '--conversation-id',
            type=int,
            required=True,
            help='Conversation ID to export',
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['markdown', 'json'],
            default='markdown',
            help='Export format (default: markdown)',
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Output file path (optional)',
        )

    def handle(self, *args, **options):
        conversation_id = options['conversation_id']
        export_format = options['format']
        output_path = options.get('output')

        try:
            conversation = Conversation.objects.prefetch_related('messages').get(id=conversation_id)
        except Conversation.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Conversation {conversation_id} not found"))
            return

        if export_format == 'markdown':
            content = self.export_to_markdown(conversation)
            extension = '.md'
        else:
            content = self.export_to_json(conversation)
            extension = '.json'

        if output_path:
            file_path = Path(output_path)
        else:
            file_path = Path(f'conversation_{conversation_id}{extension}')

        file_path.write_text(content, encoding='utf-8')
        self.stdout.write(self.style.SUCCESS(f"Exported to {file_path}"))

    def export_to_markdown(self, conversation):
        """Export conversation to Markdown format."""
        lines = [
            f"# {conversation.title or 'Untitled Conversation'}",
            "",
            f"**Created:** {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Updated:** {conversation.updated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
        ]

        for message in conversation.messages.all():
            role_emoji = "👤" if message.role == 'user' else "🤖"
            role_name = "User" if message.role == 'user' else "Assistant"
            lines.extend([
                f"## {role_emoji} {role_name}",
                "",
                message.content,
                "",
                f"*{message.created_at.strftime('%Y-%m-%d %H:%M:%S')}*",
                "",
                "---",
                "",
            ])

        return "\n".join(lines)

    def export_to_json(self, conversation):
        """Export conversation to JSON format."""
        data = {
            'id': conversation.id,
            'title': conversation.title,
            'created_at': conversation.created_at.isoformat(),
            'updated_at': conversation.updated_at.isoformat(),
            'messages': [
                {
                    'role': msg.role,
                    'content': msg.content,
                    'created_at': msg.created_at.isoformat(),
                }
                for msg in conversation.messages.all()
            ]
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

