/**
 * Screen Builder Enhancement
 *
 * Provides:
 * - CodeMirror integration for HTML/CSS/JS editors
 * - Data picker sidebar with variable browsing
 * - Click-to-insert variable functionality
 * - Autocomplete for data variables
 */

class ScreenBuilder {
    constructor() {
        this.editors = {};
        this.activeEditor = 'html';
        this.dataRegistry = null;
        this.allPaths = [];
        this.init();
    }

    async init() {
        await this.loadDataRegistry();
        this.initCodeMirror();
        this.initDataPicker();
        this.initTabSwitching();
    }

    async loadDataRegistry() {
        try {
            const response = await fetch('/api/data/registry/');
            const data = await response.json();
            if (data.success) {
                this.dataRegistry = data.registry;
                this.allPaths = data.registry.all_paths || [];
            }
        } catch (error) {
            console.error('Failed to load data registry:', error);
        }
    }

    initCodeMirror() {
        const modes = {
            html: 'htmlmixed',
            css: 'css',
            js: 'javascript'
        };

        ['html', 'css', 'js'].forEach(type => {
            const textarea = document.getElementById(`id_${type}_code`);
            if (textarea) {
                this.editors[type] = CodeMirror.fromTextArea(textarea, {
                    mode: modes[type],
                    theme: 'dracula',
                    lineNumbers: true,
                    lineWrapping: true,
                    indentUnit: 4,
                    tabSize: 4,
                    indentWithTabs: false,
                    matchBrackets: true,
                    autoCloseBrackets: true,
                    autoCloseTags: type === 'html',
                    extraKeys: {
                        'Ctrl-Space': (cm) => this.showVariableHint(cm),
                        'Tab': (cm) => {
                            if (cm.somethingSelected()) {
                                cm.indentSelection('add');
                            } else {
                                cm.replaceSelection('    ', 'end');
                            }
                        },
                        'Shift-Tab': (cm) => cm.indentSelection('subtract'),
                    }
                });

                // Setup autocomplete trigger on {{ typing
                this.editors[type].on('inputRead', (cm, change) => {
                    if (change.text[0] === '{' && change.origin === '+input') {
                        const cursor = cm.getCursor();
                        const line = cm.getLine(cursor.line);
                        const beforeCursor = line.slice(Math.max(0, cursor.ch - 2), cursor.ch);
                        if (beforeCursor === '{{') {
                            setTimeout(() => this.showVariableHint(cm), 100);
                        }
                    }
                });
            }
        });

        // Show HTML editor by default
        this.showEditor('html');
    }

    showEditor(type) {
        this.activeEditor = type;

        ['html', 'css', 'js'].forEach(t => {
            const editorDiv = document.getElementById(`${t}Editor`);
            const tabBtn = document.getElementById(`tab${t.charAt(0).toUpperCase() + t.slice(1)}`);

            if (editorDiv && tabBtn) {
                if (t === type) {
                    editorDiv.classList.remove('hidden');
                    tabBtn.classList.add('border-gray-900', 'text-gray-900', 'bg-gray-50');
                    tabBtn.classList.remove('border-transparent', 'text-gray-500');
                    // Refresh CodeMirror when showing
                    if (this.editors[t]) {
                        this.editors[t].refresh();
                    }
                } else {
                    editorDiv.classList.add('hidden');
                    tabBtn.classList.remove('border-gray-900', 'text-gray-900', 'bg-gray-50');
                    tabBtn.classList.add('border-transparent', 'text-gray-500');
                }
            }
        });
    }

    initTabSwitching() {
        ['html', 'css', 'js'].forEach(type => {
            const tabBtn = document.getElementById(`tab${type.charAt(0).toUpperCase() + type.slice(1)}`);
            if (tabBtn) {
                tabBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.showEditor(type);
                });
            }
        });
    }

    initDataPicker() {
        const container = document.getElementById('dataPickerCategories');
        const searchInput = document.getElementById('dataPickerSearch');
        const toggleBtn = document.getElementById('toggleDataPicker');
        const sidebar = document.getElementById('dataPickerSidebar');

        // Toggle sidebar
        if (toggleBtn && sidebar) {
            toggleBtn.addEventListener('click', () => {
                sidebar.classList.toggle('hidden');
                // Refresh editors when sidebar toggles (layout change)
                Object.values(this.editors).forEach(editor => editor.refresh());
            });
        }

        // Search functionality
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterDataPicker(e.target.value);
            });
        }

        // Render categories
        this.renderDataPicker(container);
    }

    renderDataPicker(container) {
        if (!container || !this.dataRegistry) return;

        container.innerHTML = '';

        this.dataRegistry.categories.forEach(category => {
            const categoryEl = this.createCategoryElement(category);
            container.appendChild(categoryEl);
        });
    }

    createCategoryElement(category) {
        const div = document.createElement('div');
        div.className = 'data-picker-category';

        // Category header
        const header = document.createElement('button');
        header.type = 'button';
        header.className = 'w-full flex items-center gap-2 px-4 py-3 text-white hover:bg-gray-800 transition-colors';
        header.innerHTML = `
            <span class="material-symbols-outlined" style="font-size: 1.2rem;">${category.icon}</span>
            <span class="font-medium">${category.name}</span>
            <span class="material-symbols-outlined ml-auto transition-transform" style="font-size: 1rem;">expand_more</span>
        `;

        // Category content
        const content = document.createElement('div');
        content.className = 'hidden';

        // Add meta fields first if any
        if (category.fields && category.fields.length > 0) {
            const fieldsContainer = document.createElement('div');
            fieldsContainer.className = 'pl-4 pb-2';
            category.fields.forEach(field => {
                const fieldEl = this.createFieldElement(field);
                fieldsContainer.appendChild(fieldEl);
            });
            content.appendChild(fieldsContainer);
        }

        // Add subcategories
        if (category.subcategories && category.subcategories.length > 0) {
            category.subcategories.forEach(sub => {
                const subEl = this.createSubcategoryElement(sub);
                content.appendChild(subEl);
            });
        }

        // Toggle content
        header.addEventListener('click', () => {
            content.classList.toggle('hidden');
            const icon = header.querySelector('.ml-auto');
            icon.style.transform = content.classList.contains('hidden') ? '' : 'rotate(180deg)';
        });

        div.appendChild(header);
        div.appendChild(content);
        return div;
    }

    createSubcategoryElement(subcategory) {
        const div = document.createElement('div');
        div.className = 'pl-2 border-l border-gray-700 ml-4';

        const header = document.createElement('button');
        header.type = 'button';
        header.className = 'w-full flex items-center gap-2 px-3 py-2 text-gray-300 hover:bg-gray-800 text-sm transition-colors';
        header.innerHTML = `
            <span class="material-symbols-outlined" style="font-size: 1rem;">${subcategory.icon}</span>
            <span>${subcategory.name}</span>
            <span class="material-symbols-outlined ml-auto transition-transform" style="font-size: 0.9rem;">chevron_right</span>
        `;

        const content = document.createElement('div');
        content.className = 'hidden pb-2';

        if (subcategory.fields) {
            subcategory.fields.forEach(field => {
                const fieldEl = this.createFieldElement(field);
                content.appendChild(fieldEl);
            });
        }

        header.addEventListener('click', () => {
            content.classList.toggle('hidden');
            const icon = header.querySelector('.ml-auto');
            icon.style.transform = content.classList.contains('hidden') ? '' : 'rotate(90deg)';
        });

        div.appendChild(header);
        div.appendChild(content);
        return div;
    }

    createFieldElement(field) {
        const div = document.createElement('div');
        div.className = 'data-picker-field px-3 py-2 mx-2 my-1 rounded cursor-pointer hover:bg-gray-800 transition-colors';
        div.setAttribute('data-field-path', field.path);
        div.setAttribute('data-field-name', field.name);
        div.setAttribute('data-is-array', field.is_array ? 'true' : 'false');

        const isArray = field.is_array;
        const typeColor = this.getTypeColor(field.data_type);

        div.innerHTML = `
            <div class="flex items-center gap-2 mb-1">
                <span class="text-white text-sm font-medium">${field.name}</span>
                ${isArray ? '<span class="text-xs bg-blue-600 text-white px-1.5 py-0.5 rounded">Array</span>' : ''}
                <span class="text-xs ${typeColor} px-1.5 py-0.5 rounded">${field.data_type}</span>
            </div>
            <code class="text-cyan-400 text-xs block mb-1">{{${field.path}}}</code>
            <p class="text-gray-500 text-xs">${field.description}</p>
            <p class="text-gray-600 text-xs mt-1">Example: <span class="text-gray-400">${field.example}</span></p>
        `;

        // Click to insert
        div.addEventListener('click', () => {
            this.insertVariable(field);
        });

        return div;
    }

    getTypeColor(dataType) {
        const colors = {
            'currency': 'bg-green-700 text-green-100',
            'number': 'bg-purple-700 text-purple-100',
            'percentage': 'bg-orange-700 text-orange-100',
            'string': 'bg-gray-600 text-gray-100',
            'date': 'bg-blue-700 text-blue-100',
            'array': 'bg-blue-600 text-blue-100',
        };
        return colors[dataType] || 'bg-gray-600 text-gray-100';
    }

    insertVariable(field) {
        const editor = this.editors[this.activeEditor];
        if (!editor) return;

        let insertText;
        if (field.is_array && field.array_item_fields) {
            // Build a loop template with common fields
            const itemFields = field.array_item_fields;
            const hasRank = itemFields.some(f => f.path === 'rank');
            const hasStoreName = itemFields.some(f => f.path === 'store_name');
            const hasValue = itemFields.some(f => f.path === 'value');

            let loopContent = '';
            if (hasRank) loopContent += '{{this.rank}}. ';
            if (hasStoreName) loopContent += '{{this.store_name}}';
            if (hasValue) loopContent += ' - {{this.value}}';

            if (!loopContent) {
                loopContent = '{{this}}';
            }

            insertText = `{{#each ${field.path}}}\n    <div>${loopContent}</div>\n{{/each}}`;
        } else {
            insertText = `{{${field.path}}}`;
        }

        const cursor = editor.getCursor();
        editor.replaceRange(insertText, cursor);
        editor.focus();

        // Position cursor after insertion
        const lines = insertText.split('\n');
        const newLine = cursor.line + lines.length - 1;
        const newCh = lines.length > 1 ? lines[lines.length - 1].length : cursor.ch + insertText.length;
        editor.setCursor({ line: newLine, ch: newCh });
    }

    showVariableHint(editor) {
        if (!this.allPaths.length) return;

        const cursor = editor.getCursor();
        const line = editor.getLine(cursor.line);

        // Find the start of the variable (after {{)
        let start = cursor.ch;
        while (start > 0 && line[start - 1] !== '{') {
            start--;
        }

        // Get what's been typed so far
        const prefix = line.slice(start, cursor.ch).toLowerCase();

        // Filter matching paths
        const matches = this.allPaths.filter(p =>
            p.toLowerCase().includes(prefix) || prefix === ''
        ).slice(0, 15); // Limit results

        if (matches.length === 0) return;

        const hints = {
            list: matches.map(path => ({
                text: path + '}}',
                displayText: path,
                className: 'cm-hint-variable'
            })),
            from: CodeMirror.Pos(cursor.line, start),
            to: cursor
        };

        CodeMirror.showHint(editor, () => hints, {
            completeSingle: false,
            alignWithWord: true
        });
    }

    filterDataPicker(query) {
        const fields = document.querySelectorAll('.data-picker-field');
        query = query.toLowerCase().trim();

        fields.forEach(field => {
            const path = (field.getAttribute('data-field-path') || '').toLowerCase();
            const name = (field.getAttribute('data-field-name') || '').toLowerCase();
            const text = field.textContent.toLowerCase();

            const visible = !query || path.includes(query) || name.includes(query) || text.includes(query);
            field.style.display = visible ? '' : 'none';
        });

        // Also show/hide parent containers based on whether they have visible children
        const subcategories = document.querySelectorAll('.data-picker-category > div:last-child > div');
        subcategories.forEach(sub => {
            const hasVisibleFields = sub.querySelectorAll('.data-picker-field:not([style*="display: none"])').length > 0;
            // Don't hide subcategories - just let fields filter
        });
    }

    // Sync CodeMirror content back to textareas before form submit
    syncToTextareas() {
        Object.entries(this.editors).forEach(([type, editor]) => {
            editor.save();
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize on screen design form pages
    if (document.getElementById('id_html_code')) {
        window.screenBuilder = new ScreenBuilder();

        // Sync CodeMirror content before form submit
        const form = document.querySelector('form');
        if (form) {
            form.addEventListener('submit', () => {
                if (window.screenBuilder) {
                    window.screenBuilder.syncToTextareas();
                }
            });
        }
    }
});
