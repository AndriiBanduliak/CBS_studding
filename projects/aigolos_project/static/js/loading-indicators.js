/**
 * Loading indicators and progress bars
 */

class LoadingIndicator {
    /**
     * Show progress bar
     */
    static showProgress(containerId, options = {}) {
        const {
            showPercentage = true,
            indeterminate = false
        } = options;

        const container = document.getElementById(containerId);
        if (!container) return null;

        // Remove existing progress bar
        const existing = container.querySelector('.progress-container');
        if (existing) existing.remove();

        // Create progress container
        const progressContainer = document.createElement('div');
        progressContainer.className = 'progress-container';
        progressContainer.innerHTML = `
            <div class="progress-bar-wrapper">
                <div class="progress-bar ${indeterminate ? 'indeterminate' : ''}" id="${containerId}-progress">
                    ${indeterminate ? '' : '<div class="progress-fill" id="${containerId}-progress-fill"></div>'}
                </div>
                ${showPercentage && !indeterminate ? `<span class="progress-text" id="${containerId}-progress-text">0%</span>` : ''}
            </div>
            ${indeterminate ? '<div class="progress-spinner"></div>' : ''}
        `;
        container.appendChild(progressContainer);
        container.style.display = 'block';

        return {
            update: (percent) => {
                if (indeterminate) return;
                const fill = document.getElementById(`${containerId}-progress-fill`);
                const text = document.getElementById(`${containerId}-progress-text`);
                if (fill) {
                    fill.style.width = `${Math.min(100, Math.max(0, percent))}%`;
                }
                if (text) {
                    text.textContent = `${Math.round(percent)}%`;
                }
            },
            hide: () => {
                progressContainer.remove();
                container.style.display = 'none';
            }
        };
    }

    /**
     * Show skeleton loader
     */
    static showSkeleton(containerId, count = 3) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = '';
        for (let i = 0; i < count; i++) {
            const skeleton = document.createElement('div');
            skeleton.className = 'skeleton-loader';
            container.appendChild(skeleton);
        }
    }

    /**
     * Hide skeleton loader
     */
    static hideSkeleton(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const skeletons = container.querySelectorAll('.skeleton-loader');
        skeletons.forEach(s => s.remove());
    }

    /**
     * Show spinner
     */
    static showSpinner(elementId) {
        const element = document.getElementById(elementId);
        if (!element) return;

        element.innerHTML = '<div class="spinner"></div>';
        element.style.display = 'block';
    }

    /**
     * Hide spinner
     */
    static hideSpinner(elementId) {
        const element = document.getElementById(elementId);
        if (!element) return;

        element.innerHTML = '';
        element.style.display = 'none';
    }
}

