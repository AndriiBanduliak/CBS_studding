/**
 * Drag and drop functionality for file uploads
 */

class DragDropManager {
    constructor() {
        this.dropZones = [];
        this.init();
    }

    init() {
        // Find all drop zones
        const audioUpload = document.getElementById('audio-file')?.parentElement;
        if (audioUpload) {
            this.addDropZone(audioUpload, (files) => {
                const audioFile = files[0];
                if (audioFile && typeof transcribeAudio === 'function') {
                    // Update file input
                    const fileInput = document.getElementById('audio-file');
                    if (fileInput) {
                        const dataTransfer = new DataTransfer();
                        dataTransfer.items.add(audioFile);
                        fileInput.files = dataTransfer.files;
                        
                        // Trigger change event
                        const event = new Event('change', { bubbles: true });
                        fileInput.dispatchEvent(event);
                    }
                }
            });
        }
    }

    addDropZone(element, onDrop) {
        if (!element) return;

        element.classList.add('drop-zone');
        this.dropZones.push({ element, onDrop });

        element.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            element.classList.add('drag-over');
        });

        element.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            element.classList.remove('drag-over');
        });

        element.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            element.classList.remove('drag-over');

            const files = Array.from(e.dataTransfer.files);
            if (files.length > 0 && onDrop) {
                onDrop(files);
            }
        });
    }
}

// Initialize drag and drop
document.addEventListener('DOMContentLoaded', () => {
    const dragDropManager = new DragDropManager();
});

