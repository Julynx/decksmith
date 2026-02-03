document.addEventListener('DOMContentLoaded', function () {
    // --- Initialization ---

    // Initialize Split.js
    Split(['#left-pane', '#right-pane'], {
        sizes: [50, 50],
        minSize: 200,
        gutterSize: 10,
        cursor: 'col-resize'
    });

    Split(['#yaml-pane', '#csv-pane'], {
        direction: 'vertical',
        sizes: [50, 50],
        minSize: 100,
        gutterSize: 10,
        cursor: 'row-resize'
    });

    // Initialize Ace Editors
    const yamlEditor = ace.edit("yaml-editor");
    yamlEditor.setTheme("ace/theme/tomorrow_night");
    yamlEditor.session.setMode("ace/mode/yaml");
    yamlEditor.setOptions({
        fontSize: "12pt",
        showPrintMargin: false,
    });

    const csvEditor = ace.edit("csv-editor");
    csvEditor.setTheme("ace/theme/tomorrow_night");
    csvEditor.session.setMode("ace/mode/text");
    csvEditor.setOptions({
        fontSize: "12pt",
        showPrintMargin: false,
    });

    // --- Elements ---
    const elements = {
        cardSelector: document.getElementById('card-selector'),
        buildBtn: document.getElementById('build-btn'),
        exportBtn: document.getElementById('export-btn'),
        previewImage: document.getElementById('preview-image'),
        placeholderText: document.getElementById('placeholder-text'),
        loadingIndicator: document.getElementById('loading-indicator'),
        statusBar: document.getElementById('status-bar'),
        statusText: document.getElementById('status-text'),
        statusSpinner: document.getElementById('status-spinner'),
        statusIcon: document.getElementById('status-icon'),
        statusLine: document.getElementById('status-line'),
        toastContainer: document.getElementById('toast-container'),

        // Project controls
        currentProjectPath: document.getElementById('current-project-path'),
        openProjectBtn: document.getElementById('open-project-btn'),
        newProjectBtn: document.getElementById('new-project-btn'),
        closeProjectBtn: document.getElementById('close-project-btn'),
        pathModal: document.getElementById('path-modal'),
        modalTitle: document.getElementById('modal-title'),
        projectPathLabel: document.getElementById('project-path-label'),
        projectPathInput: document.getElementById('project-path-input'),
        projectNameGroup: document.getElementById('project-name-group'),
        projectNameInput: document.getElementById('project-name-input'),
        modalCancelBtn: document.getElementById('modal-cancel-btn'),
        modalConfirmBtn: document.getElementById('modal-confirm-btn'),

        // Welcome screen & Browse
        welcomeScreen: document.getElementById('welcome-screen'),
        welcomeOpenBtn: document.getElementById('welcome-open-btn'),
        welcomeNewBtn: document.getElementById('welcome-new-btn'),
        browseBtn: document.getElementById('browse-btn'),

        // Shutdown Screen
        shutdownScreen: document.getElementById('shutdown-screen'),
        shutdownReason: document.getElementById('shutdown-reason'),

        // Export Modal
        exportModal: document.getElementById('export-modal'),
        exportFilename: document.getElementById('export-filename'),
        exportPageSize: document.getElementById('export-page-size'),
        exportWidth: document.getElementById('export-width'),
        exportHeight: document.getElementById('export-height'),
        exportGap: document.getElementById('export-gap'),
        exportMarginX: document.getElementById('export-margin-x'),
        exportMarginY: document.getElementById('export-margin-y'),
        exportCancelBtn: document.getElementById('export-cancel-btn'),
        exportConfirmBtn: document.getElementById('export-confirm-btn'),
    };

    // --- State ---
    let state = {
        currentCardIndex: -1,
        isDirty: false,
        modalMode: 'open', // 'open' or 'new'
        isPreviewing: false,
        pendingPreview: false,
        isProjectOpen: false,
        hasSyntaxError: false
    };

    // --- Annotation Handler ---
    function checkAnnotations() {
        // Wait slightly for Ace to update annotations
        setTimeout(() => {
            const annotations = yamlEditor.getSession().getAnnotations();
            const errors = annotations.filter(a => a.type === 'error');

            if (errors.length > 0) {
                state.hasSyntaxError = true;
                // Use the first error message
                setStatus(`YAML Syntax Error: ${errors[0].text} (Line ${errors[0].row + 1})`, 'error');
            } else {
                if (state.hasSyntaxError) {
                    state.hasSyntaxError = false;
                    setStatus('Ready'); // Clear error status
                }
            }
        }, 100);
    }

    // --- UI Helpers ---

    function showShutdownScreen(reason) {
        elements.shutdownReason.textContent = reason || 'The DeckSmith service stopped.';
        elements.shutdownScreen.classList.remove('hidden');
    }

    function showNotification(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;

        elements.toastContainer.appendChild(toast);

        requestAnimationFrame(() => {
            toast.classList.add('show');
        });

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 3000);
    }

    function updateStatusLine(status) {
        elements.statusLine.className = 'status-line';
        if (status) {
            elements.statusLine.classList.add(status);
        }
    }

    function setStatus(message, type = null) {
        elements.statusText.textContent = message;

        // Reset status bar state
        elements.statusBar.classList.remove('processing', 'success', 'error');
        elements.statusSpinner.classList.add('hidden');
        elements.statusIcon.classList.remove('hidden');

        // Reset icon to default
        elements.statusIcon.className = 'fa-solid fa-circle-info fa-fw';

        if (type === 'processing') {
            elements.statusBar.classList.add('processing');
            elements.statusSpinner.classList.remove('hidden');
            elements.statusIcon.classList.add('hidden');
            updateStatusLine('loading');
        } else if (type === 'success') {
            elements.statusBar.classList.add('success');
            updateStatusLine('success');
        } else if (type === 'error') {
            elements.statusBar.classList.add('error');
            updateStatusLine('error');
            // Change icon to danger
            elements.statusIcon.className = 'fa-solid fa-triangle-exclamation fa-fw';
        } else {
            if (type) updateStatusLine(type);
        }
    }

    // --- API Interactions ---

    function loadCurrentProject() {
        fetch('/api/project/current')
            .then(response => response.json())
            .then(data => {
                if (data.path) {
                    state.isProjectOpen = true;
                    elements.currentProjectPath.textContent = data.path;
                    elements.currentProjectPath.title = data.path;
                    elements.welcomeScreen.classList.add('hidden');
                    loadInitialData();
                } else {
                    state.isProjectOpen = false;
                    elements.currentProjectPath.textContent = 'No project selected';
                    elements.welcomeScreen.classList.remove('hidden');
                }
            })
            .catch(err => console.error('Error loading project path:', err));
    }

    function loadInitialData() {
        fetch('/api/load')
            .then(response => response.json())
            .then(data => {
                yamlEditor.setValue(data.yaml || '', -1);
                csvEditor.setValue(data.csv || '', -1);
                loadCards();
            })
            .catch(err => console.error('Error loading data:', err));
    }

    function loadCards() {
        fetch('/api/cards')
            .then(response => response.json())
            .then(cards => {
                elements.cardSelector.innerHTML = '<option value="-1">Select a card...</option>';
                cards.forEach((card, index) => {
                    const option = document.createElement('option');
                    option.value = index;
                    const label = card.Name || card.name || card.Title || card.title || `Card ${index + 1}`;
                    option.textContent = `${index + 1}: ${label}`;
                    elements.cardSelector.appendChild(option);
                });

                if (state.currentCardIndex >= 0 && state.currentCardIndex < cards.length) {
                    elements.cardSelector.value = state.currentCardIndex;
                } else if (cards.length > 0) {
                    elements.cardSelector.value = 0;
                    updatePreview();
                }
            })
            .catch(err => console.error('Error loading cards:', err));
    }

    function updatePreview() {
        const index = parseInt(elements.cardSelector.value);
        if (index === -1) {
            elements.previewImage.classList.add('hidden');
            elements.placeholderText.classList.remove('hidden');
            return;
        }

        if (state.isPreviewing) {
            state.pendingPreview = true;
            return;
        }

        state.isDirty = false;
        state.currentCardIndex = index;
        state.isPreviewing = true;
        state.pendingPreview = false;

        elements.loadingIndicator.classList.remove('hidden');
        elements.placeholderText.classList.add('hidden');
        setStatus('Generating preview...', 'loading');

        const payload = {
            yaml: yamlEditor.getValue(),
            csv: csvEditor.getValue()
        };

        fetch(`/api/preview/${index}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.error || 'Preview failed'); });
                }
                return response.blob();
            })
            .then(blob => {
                const url = URL.createObjectURL(blob);
                elements.previewImage.src = url;
                elements.previewImage.onload = () => {
                    elements.loadingIndicator.classList.add('hidden');
                    elements.previewImage.classList.remove('hidden');
                    setStatus('Preview updated');
                    updateStatusLine('success');
                };
            })
            .catch(err => {
                elements.loadingIndicator.classList.add('hidden');
                setStatus(`Error: ${err.message}`, 'error');
                console.error(err);
            })
            .finally(() => {
                state.isPreviewing = false;
                if (state.pendingPreview) {
                    updatePreview();
                }
            });
    }

    function autoSave() {
        if (!state.isProjectOpen) return;

        if (!elements.statusText.textContent.includes('preview')) {
            setStatus('Saving...');
        }

        const payload = {
            yaml: yamlEditor.getValue(),
            csv: csvEditor.getValue()
        };

        fetch('/api/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
            .then(response => response.json())
            .then(data => {
                // if (!elements.statusText.textContent.includes('preview')) {
                //     setStatus('Saved');
                // }
                loadCards();
            })
            .catch(err => {
                setStatus('Error saving');
                console.error(err);
            });
    }

    function buildDeck() {
        setStatus('Building deck...', 'processing');
        const payload = {
            yaml: yamlEditor.getValue(),
            csv: csvEditor.getValue()
        };

        return fetch('/api/build', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) throw new Error(data.error);
                setStatus(data.message, 'success');
                showNotification(data.message, 'success');
                return data;
            })
            .catch(err => {
                setStatus('Build failed: ' + err.message, 'error');
                showNotification('Build failed: ' + err.message, 'error');
                throw err;
            });
    }

    function showExportModal() {
        elements.exportModal.classList.remove('hidden');
    }

    function hideExportModal() {
        elements.exportModal.classList.add('hidden');
    }

    function handleExportConfirm() {
        const params = {
            filename: elements.exportFilename.value,
            page_size: elements.exportPageSize.value,
            width: parseFloat(elements.exportWidth.value),
            height: parseFloat(elements.exportHeight.value),
            gap: parseFloat(elements.exportGap.value),
            margin_x: parseFloat(elements.exportMarginX.value),
            margin_y: parseFloat(elements.exportMarginY.value)
        };

        hideExportModal();

        // Chain build then export
        buildDeck()
            .then(() => {
                exportPdf(params);
            })
            .catch(() => {
                // Build failed, error already handled by buildDeck UI updates
                console.log('Export cancelled due to build failure');
            });
    }

    function exportPdf(params) {
        setStatus('Exporting PDF...', 'processing');
        fetch('/api/export', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) throw new Error(data.error);
                setStatus(data.message, 'success');
                showNotification(data.message, 'success');
            })
            .catch(err => {
                setStatus('Export failed: ' + err.message, 'error');
                showNotification('Export failed: ' + err.message, 'error');
            });
    }

    // --- Project Management ---

    function showModal(mode) {
        state.modalMode = mode;
        elements.modalTitle.textContent = mode === 'open' ? 'Open Project' : 'New Project';
        elements.projectPathInput.value = '';
        elements.projectNameInput.value = '';
        elements.projectPathInput.classList.remove('input-error');
        elements.projectNameInput.classList.remove('input-error');
        elements.pathModal.classList.remove('hidden');

        if (mode === 'new') {
            elements.projectPathLabel.textContent = 'Store project in:';
            elements.projectNameGroup.classList.remove('hidden');
            elements.projectPathInput.placeholder = 'Loading default path...';

            fetch('/api/system/default-path')
                .then(response => response.json())
                .then(data => {
                    if (data.path) {
                        elements.projectPathInput.value = data.path;
                    }
                })
                .catch(err => console.error('Error fetching default path:', err));

            elements.projectNameInput.focus();
        } else {
            elements.projectPathLabel.textContent = 'Folder Path:';
            elements.projectNameGroup.classList.add('hidden');
            elements.projectPathInput.placeholder = 'e.g. C:/Projects/MyDeck';
            elements.projectPathInput.focus();
        }
    }

    function hideModal() {
        elements.pathModal.classList.add('hidden');
    }

    function browseFolder() {
        fetch('/api/system/browse', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.path) {
                    elements.projectPathInput.value = data.path;
                }
            })
            .catch(err => console.error('Error browsing:', err));
    }

    function openProject(path) {
        setStatus('Opening project...');
        fetch('/api/project/select', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: path })
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) throw new Error(data.error);

                state.isProjectOpen = true;
                elements.currentProjectPath.textContent = data.path;
                elements.currentProjectPath.title = data.path;

                // showNotification('Project opened', 'success');
                setStatus('Ready');

                loadInitialData();
                elements.welcomeScreen.classList.add('hidden');
            })
            .catch(err => {
                setStatus('Error: ' + err.message, 'error');
            });
    }

    function handleDirectOpen() {
        fetch('/api/system/browse', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.path) {
                    openProject(data.path);
                }
            })
            .catch(err => console.error('Error browsing:', err));
    }

    // Clear error on input
    elements.projectPathInput.addEventListener('input', () => {
        elements.projectPathInput.classList.remove('input-error');
    });

    elements.projectNameInput.addEventListener('input', () => {
        elements.projectNameInput.classList.remove('input-error');
    });

    function handleProjectAction() {
        let path = elements.projectPathInput.value.trim();
        if (!path) {
            elements.projectPathInput.classList.add('input-error');
            // showNotification('Please enter a path', 'error');
            return;
        }

        if (state.modalMode === 'new') {
            const name = elements.projectNameInput.value.trim();
            if (!name) {
                elements.projectNameInput.classList.add('input-error');
                // showNotification('Please enter a project name', 'error');
                return;
            }
            const separator = path.includes('\\') ? '\\' : '/';
            path = path.endsWith(separator) ? path + name : path + separator + name;
        }

        const endpoint = state.modalMode === 'open' ? '/api/project/select' : '/api/project/create';

        setStatus(state.modalMode === 'open' ? 'Opening project...' : 'Creating project...');

        fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: path })
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) throw new Error(data.error);

                hideModal();
                state.isProjectOpen = true;
                elements.currentProjectPath.textContent = data.path;
                elements.currentProjectPath.title = data.path;

                // showNotification(state.modalMode === 'open' ? 'Project opened' : 'Project created', 'success');
                setStatus('Ready');

                // Reload data
                loadInitialData();
                elements.welcomeScreen.classList.add('hidden');
            })
            .catch(err => {
                setStatus('Error: ' + err.message, 'error');
            });
    }

    function closeProject() {
        fetch('/api/project/close', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                state.isProjectOpen = false;
                elements.currentProjectPath.textContent = 'No project selected';
                elements.currentProjectPath.title = '';

                // Clear editors
                yamlEditor.setValue('', -1);
                csvEditor.setValue('', -1);
                state.isDirty = false; // Reset dirty flag after clearing editors

                elements.cardSelector.innerHTML = '<option value="-1">Select a card...</option>';
                elements.previewImage.classList.add('hidden');
                elements.placeholderText.classList.remove('hidden');

                elements.welcomeScreen.classList.remove('hidden');
                // showNotification('Project closed', 'info');
            })
            .catch(err => console.error('Error closing project:', err));
    }

    // --- Event Listeners ---

    elements.cardSelector.addEventListener('change', updatePreview);
    elements.buildBtn.addEventListener('click', buildDeck);
    elements.exportBtn.addEventListener('click', showExportModal);

    elements.exportCancelBtn.addEventListener('click', hideExportModal);
    elements.exportConfirmBtn.addEventListener('click', handleExportConfirm);
    elements.exportModal.querySelector('.modal-overlay').addEventListener('click', hideExportModal);

    elements.openProjectBtn.addEventListener('click', handleDirectOpen);
    elements.newProjectBtn.addEventListener('click', () => showModal('new'));
    elements.closeProjectBtn.addEventListener('click', closeProject);
    elements.modalCancelBtn.addEventListener('click', hideModal);
    elements.modalConfirmBtn.addEventListener('click', handleProjectAction);
    elements.pathModal.querySelector('.modal-overlay').addEventListener('click', hideModal);

    elements.welcomeOpenBtn.addEventListener('click', handleDirectOpen);
    elements.welcomeNewBtn.addEventListener('click', () => showModal('new'));
    elements.browseBtn.addEventListener('click', browseFolder);

    const markDirty = () => {
        state.isDirty = true;
    };

    yamlEditor.session.on('change', markDirty);
    yamlEditor.session.on('changeAnnotation', checkAnnotations);
    csvEditor.session.on('change', markDirty);

    // Auto-save loop
    setInterval(() => {
        if (state.isDirty) {
            autoSave();
            if (state.currentCardIndex !== -1) {
                updatePreview();
            } else {
                state.isDirty = false;
            }
        }
    }, 2000);

    // Start
    loadCurrentProject();

    // Shutdown
    window.addEventListener('beforeunload', () => {
        navigator.sendBeacon('/api/shutdown');
    });

    // SSE for Server Events (Shutdown)
    const evtSource = new EventSource("/api/events");
    evtSource.onmessage = (e) => {
        // Ignore keepalive
        if (e.data === ': keepalive') return;

        try {
            const data = JSON.parse(e.data);
            if (data.type === 'shutdown') {
                showShutdownScreen(data.reason);
                evtSource.close();
            }
        } catch (err) {
            // Ignore parse errors or keepalives that might slip through
        }
    };
});
