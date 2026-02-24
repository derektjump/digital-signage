/**
 * Visual Builder for Digital Signage
 * Uses GrapesJS for drag-and-drop screen design
 */

// Alpine.js component for Visual Builder
function visualBuilder() {
    return {
        editor: null,
        designName: '',
        designSlug: '',
        dataSearch: '',
        pickerSearch: '',
        showDataPicker: false,
        currentPickerCallback: null,
        dataRegistry: null,
        componentRegistry: null,

        init() {
            const config = window.VISUAL_BUILDER_CONFIG;
            this.designName = config.designName || 'Untitled Design';
            this.designSlug = config.designSlug || '';
            this.dataRegistry = config.dataRegistry;
            this.componentRegistry = config.componentRegistry;

            // Initialize GrapesJS after DOM is ready
            // Use setTimeout to ensure DOM is fully rendered
            setTimeout(() => {
                this.initGrapesJS();
                this.renderDataFields();
            }, 100);
        },

        initGrapesJS() {
            const config = window.VISUAL_BUILDER_CONFIG;

            this.editor = grapesjs.init({
                container: '#gjs-editor',
                fromElement: false,
                height: '100%',
                width: 'auto',
                storageManager: false,

                // Canvas configuration
                canvas: {
                    styles: [
                        'https://fonts.googleapis.com/css2?family=Onest:wght@200;400;500;600;700&family=Oxanium:wght@200;400;500;600;700&display=swap',
                    ],
                },

                // Panels configuration
                panels: {
                    defaults: []
                },

                // Block manager
                blockManager: {
                    appendTo: '#blocks-container',
                },

                // Trait manager
                traitManager: {
                    appendTo: '#traits-container',
                },

                // Style manager
                styleManager: {
                    appendTo: '#styles-container',
                    sectors: [
                        {
                            name: 'Layout',
                            open: true,
                            properties: [
                                'display', 'flex-direction', 'justify-content', 'align-items',
                                'width', 'height', 'padding', 'margin'
                            ]
                        },
                        {
                            name: 'Typography',
                            open: false,
                            properties: [
                                'font-family', 'font-size', 'font-weight', 'color', 'text-align'
                            ]
                        },
                        {
                            name: 'Background',
                            open: false,
                            properties: [
                                'background-color', 'background-image', 'background-size'
                            ]
                        },
                        {
                            name: 'Border',
                            open: false,
                            properties: [
                                'border', 'border-radius', 'box-shadow'
                            ]
                        }
                    ]
                },

                // Layer manager
                layerManager: {
                    appendTo: '#layers-container',
                },

                // Device manager
                deviceManager: {
                    devices: [
                        { name: 'TV Screen', width: '1920px' },
                        { name: 'Tablet', width: '768px' },
                    ]
                },
            });

            // Register custom components
            this.registerComponents();

            // Register custom blocks
            this.registerBlocks();

            // Register custom traits
            this.registerTraits();

            // Load existing content if editing
            if (config.visualBuilderData) {
                this.editor.loadProjectData(config.visualBuilderData);
            } else if (config.htmlCode) {
                this.editor.setComponents(config.htmlCode);
                this.editor.setStyle(config.cssCode || '');
            }

            // Listen for component selection
            this.editor.on('component:selected', (component) => {
                document.querySelector('.vb-no-selection')?.classList.add('hidden');
            });

            this.editor.on('component:deselected', () => {
                const noSelection = document.querySelector('.vb-no-selection');
                if (noSelection && !this.editor.getSelected()) {
                    noSelection.classList.remove('hidden');
                }
            });
        },

        registerComponents() {
            const editor = this.editor;
            const dc = editor.DomComponents;

            // Leaderboard Component
            dc.addType('leaderboard', {
                model: {
                    defaults: {
                        tagName: 'div',
                        draggable: true,
                        droppable: false,
                        attributes: { class: 'vb-leaderboard', 'data-component': 'leaderboard' },
                        traits: [
                            { type: 'text', name: 'title', label: 'Title', default: 'Top Performers' },
                            { type: 'data-binding', name: 'dataSource', label: 'Data Source', bindingType: 'array' },
                            { type: 'number', name: 'maxItems', label: 'Max Items', default: 5, min: 1, max: 20 },
                            { type: 'checkbox', name: 'showBadges', label: 'Show Rank Badges', default: true },
                        ],
                        components: `
                            <div class="leaderboard-header">
                                <h2 class="leaderboard-title">Top Performers</h2>
                            </div>
                            <div class="leaderboard-list">
                                <div class="leaderboard-item rank-1">
                                    <div class="rank-badge">1</div>
                                    <span class="store-name">Store Name</span>
                                    <span class="store-value">$10,000</span>
                                </div>
                                <div class="leaderboard-item rank-2">
                                    <div class="rank-badge">2</div>
                                    <span class="store-name">Store Name</span>
                                    <span class="store-value">$9,500</span>
                                </div>
                                <div class="leaderboard-item rank-3">
                                    <div class="rank-badge">3</div>
                                    <span class="store-name">Store Name</span>
                                    <span class="store-value">$8,200</span>
                                </div>
                            </div>
                        `,
                        styles: `
                            .vb-leaderboard {
                                background: rgba(255,255,255,0.03);
                                border: 1px solid rgba(255,255,255,0.1);
                                border-radius: 12px;
                                padding: 1.5rem;
                                font-family: 'Onest', sans-serif;
                            }
                            .leaderboard-title {
                                color: #fff;
                                font-size: 1.25rem;
                                font-weight: 600;
                                margin: 0 0 1rem 0;
                            }
                            .leaderboard-item {
                                display: flex;
                                align-items: center;
                                padding: 0.75rem 1rem;
                                background: rgba(0,0,0,0.2);
                                border-radius: 8px;
                                margin-bottom: 0.5rem;
                            }
                            .leaderboard-item.rank-1 { background: linear-gradient(90deg, rgba(255,215,0,0.2) 0%, rgba(0,0,0,0.2) 100%); }
                            .leaderboard-item.rank-2 { background: linear-gradient(90deg, rgba(192,192,192,0.2) 0%, rgba(0,0,0,0.2) 100%); }
                            .leaderboard-item.rank-3 { background: linear-gradient(90deg, rgba(205,127,50,0.2) 0%, rgba(0,0,0,0.2) 100%); }
                            .rank-badge {
                                width: 32px;
                                height: 32px;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                background: rgba(100,52,248,0.3);
                                border: 2px solid rgba(100,52,248,0.5);
                                border-radius: 50%;
                                color: #fff;
                                font-weight: bold;
                                font-size: 0.875rem;
                                margin-right: 1rem;
                            }
                            .leaderboard-item.rank-1 .rank-badge { background: rgba(255,215,0,0.3); border-color: rgba(255,215,0,0.5); }
                            .leaderboard-item.rank-2 .rank-badge { background: rgba(192,192,192,0.3); border-color: rgba(192,192,192,0.5); }
                            .leaderboard-item.rank-3 .rank-badge { background: rgba(205,127,50,0.3); border-color: rgba(205,127,50,0.5); }
                            .store-name { flex: 1; color: #fff; }
                            .store-value { color: #4ade80; font-weight: 600; }
                        `
                    },
                    init() {
                        this.on('change:title', this.updateTitle);
                    },
                    updateTitle() {
                        const titleEl = this.find('.leaderboard-title')[0];
                        if (titleEl) {
                            titleEl.set('content', this.get('title') || 'Top Performers');
                        }
                    }
                }
            });

            // Stat Card Component
            dc.addType('stat-card', {
                model: {
                    defaults: {
                        tagName: 'div',
                        draggable: true,
                        droppable: false,
                        attributes: { class: 'vb-stat-card', 'data-component': 'stat-card' },
                        traits: [
                            { type: 'text', name: 'label', label: 'Label', default: 'Metric' },
                            { type: 'data-binding', name: 'value', label: 'Value', bindingType: 'scalar' },
                            { type: 'text', name: 'subtext', label: 'Sub Text', default: '' },
                            {
                                type: 'select',
                                name: 'variant',
                                label: 'Style',
                                options: [
                                    { value: 'default', name: 'Default' },
                                    { value: 'primary', name: 'Primary (Purple)' },
                                    { value: 'accent', name: 'Accent (Cyan)' },
                                    { value: 'success', name: 'Success (Green)' },
                                ],
                                default: 'default'
                            }
                        ],
                        components: `
                            <div class="stat-label">Metric</div>
                            <div class="stat-value">$0</div>
                            <div class="stat-subtext"></div>
                        `,
                        styles: `
                            .vb-stat-card {
                                background: rgba(255,255,255,0.03);
                                backdrop-filter: blur(10px);
                                border: 1px solid rgba(255,255,255,0.1);
                                border-radius: 12px;
                                padding: 1.25rem;
                                font-family: 'Onest', sans-serif;
                                min-width: 150px;
                            }
                            .stat-label {
                                font-size: 0.75rem;
                                color: #9ca3af;
                                text-transform: uppercase;
                                letter-spacing: 0.05em;
                                margin-bottom: 0.5rem;
                            }
                            .stat-value {
                                font-size: 2rem;
                                font-weight: 600;
                                color: #fff;
                                line-height: 1.2;
                            }
                            .vb-stat-card.primary .stat-value { color: #a78bfa; }
                            .vb-stat-card.accent .stat-value { color: #00f0ff; }
                            .vb-stat-card.success .stat-value { color: #4ade80; }
                            .stat-subtext {
                                font-size: 0.75rem;
                                color: #6b7280;
                                margin-top: 0.25rem;
                            }
                        `
                    },
                    init() {
                        this.on('change:label', this.updateLabel);
                        this.on('change:variant', this.updateVariant);
                    },
                    updateLabel() {
                        const labelEl = this.find('.stat-label')[0];
                        if (labelEl) {
                            labelEl.set('content', this.get('label') || 'Metric');
                        }
                    },
                    updateVariant() {
                        const variant = this.get('variant');
                        this.setClass(['vb-stat-card', variant !== 'default' ? variant : ''].filter(Boolean));
                    }
                }
            });

            // Metrics Grid Component
            dc.addType('metrics-grid', {
                model: {
                    defaults: {
                        tagName: 'div',
                        draggable: true,
                        droppable: true,
                        attributes: { class: 'vb-metrics-grid', 'data-component': 'metrics-grid' },
                        traits: [
                            { type: 'number', name: 'columns', label: 'Columns', default: 4, min: 1, max: 6 },
                            { type: 'text', name: 'gap', label: 'Gap', default: '1rem' },
                        ],
                        styles: `
                            .vb-metrics-grid {
                                display: grid;
                                grid-template-columns: repeat(4, 1fr);
                                gap: 1rem;
                                padding: 1rem;
                            }
                        `
                    },
                    init() {
                        this.on('change:columns', this.updateColumns);
                        this.on('change:gap', this.updateGap);
                    },
                    updateColumns() {
                        const cols = this.get('columns') || 4;
                        this.addStyle({ 'grid-template-columns': `repeat(${cols}, 1fr)` });
                    },
                    updateGap() {
                        const gap = this.get('gap') || '1rem';
                        this.addStyle({ 'gap': gap });
                    }
                }
            });

            // Ticker Component
            dc.addType('ticker', {
                model: {
                    defaults: {
                        tagName: 'div',
                        draggable: true,
                        droppable: false,
                        attributes: { class: 'vb-ticker', 'data-component': 'ticker' },
                        traits: [
                            { type: 'data-binding', name: 'items', label: 'Items', bindingType: 'array' },
                            { type: 'number', name: 'speed', label: 'Speed (px/s)', default: 50, min: 10, max: 200 },
                            {
                                type: 'select',
                                name: 'direction',
                                label: 'Direction',
                                options: [
                                    { value: 'left', name: 'Left' },
                                    { value: 'right', name: 'Right' },
                                ],
                                default: 'left'
                            }
                        ],
                        components: `
                            <div class="ticker-content">
                                <span class="ticker-item">Breaking News: This is a sample ticker message</span>
                                <span class="ticker-separator">•</span>
                                <span class="ticker-item">Another important announcement here</span>
                                <span class="ticker-separator">•</span>
                            </div>
                        `,
                        styles: `
                            .vb-ticker {
                                background: rgba(100,52,248,0.1);
                                border-top: 1px solid rgba(100,52,248,0.3);
                                border-bottom: 1px solid rgba(100,52,248,0.3);
                                padding: 0.75rem 0;
                                overflow: hidden;
                                white-space: nowrap;
                            }
                            .ticker-content {
                                display: inline-block;
                                animation: ticker-scroll 20s linear infinite;
                            }
                            .ticker-item {
                                color: #fff;
                                font-family: 'Onest', sans-serif;
                                font-size: 0.875rem;
                            }
                            .ticker-separator {
                                color: #6434f8;
                                margin: 0 2rem;
                            }
                            @keyframes ticker-scroll {
                                0% { transform: translateX(0); }
                                100% { transform: translateX(-50%); }
                            }
                        `
                    }
                }
            });
        },

        registerBlocks() {
            const bm = this.editor.BlockManager;

            bm.add('leaderboard', {
                label: 'Leaderboard',
                category: 'Data Display',
                content: { type: 'leaderboard' },
                media: '<span class="material-symbols-outlined" style="font-size:32px;color:#6434f8;">leaderboard</span>',
            });

            bm.add('stat-card', {
                label: 'Stat Card',
                category: 'Metrics',
                content: { type: 'stat-card' },
                media: '<span class="material-symbols-outlined" style="font-size:32px;color:#6434f8;">analytics</span>',
            });

            bm.add('metrics-grid', {
                label: 'Metrics Grid',
                category: 'Layout',
                content: { type: 'metrics-grid' },
                media: '<span class="material-symbols-outlined" style="font-size:32px;color:#6434f8;">grid_view</span>',
            });

            bm.add('ticker', {
                label: 'Ticker',
                category: 'Animation',
                content: { type: 'ticker' },
                media: '<span class="material-symbols-outlined" style="font-size:32px;color:#6434f8;">subtitles</span>',
            });

            // Basic layout blocks
            bm.add('section', {
                label: 'Section',
                category: 'Layout',
                content: '<section class="vb-section" style="padding: 2rem; background: rgba(255,255,255,0.02); border-radius: 12px;"></section>',
                media: '<span class="material-symbols-outlined" style="font-size:32px;color:#6434f8;">crop_landscape</span>',
            });

            bm.add('heading', {
                label: 'Heading',
                category: 'Basic',
                content: '<h2 style="color: #fff; font-family: Oxanium, sans-serif; font-size: 1.5rem; margin: 0;">Heading Text</h2>',
                media: '<span class="material-symbols-outlined" style="font-size:32px;color:#6434f8;">title</span>',
            });

            bm.add('text', {
                label: 'Text',
                category: 'Basic',
                content: '<p style="color: #9ca3af; font-family: Onest, sans-serif; font-size: 1rem; margin: 0;">Your text here</p>',
                media: '<span class="material-symbols-outlined" style="font-size:32px;color:#6434f8;">text_fields</span>',
            });
        },

        registerTraits() {
            const tm = this.editor.TraitManager;
            const self = this;

            // Custom data-binding trait
            tm.addType('data-binding', {
                createInput({ trait }) {
                    const el = document.createElement('div');
                    el.className = 'data-binding-trait';
                    el.innerHTML = `
                        <div style="display:flex;gap:0.5rem;">
                            <input type="text" class="data-binding-input gjs-field" style="flex:1;" readonly placeholder="Click to select...">
                            <button type="button" class="vb-btn vb-btn-secondary" style="padding:0.25rem 0.5rem;">
                                <span class="material-symbols-outlined" style="font-size:1rem;">database</span>
                            </button>
                        </div>
                    `;

                    const input = el.querySelector('.data-binding-input');
                    const btn = el.querySelector('button');

                    btn.addEventListener('click', () => {
                        const bindingType = trait.get('bindingType') || 'any';
                        self.openDataPicker(bindingType, (selected) => {
                            input.value = selected;
                            input.dispatchEvent(new Event('change'));
                        });
                    });

                    return el;
                },
                onEvent({ elInput, component, trait }) {
                    const input = elInput.querySelector('.data-binding-input');
                    component.set(trait.get('name'), input.value);
                },
                onUpdate({ elInput, component, trait }) {
                    const input = elInput.querySelector('.data-binding-input');
                    input.value = component.get(trait.get('name')) || '';
                }
            });
        },

        renderDataFields() {
            const container = document.getElementById('data-fields-container');
            if (!container || !this.dataRegistry) return;

            let html = '';
            const categories = this.dataRegistry.categories || [];

            categories.forEach(category => {
                html += `
                    <div class="vb-data-category" x-data="{ open: false }">
                        <div class="vb-data-category-header" @click="open = !open">
                            <span class="material-symbols-outlined">${category.icon || 'folder'}</span>
                            <span class="vb-data-category-name">${category.name}</span>
                            <span class="material-symbols-outlined" x-text="open ? 'expand_less' : 'expand_more'" style="margin-left:auto;font-size:1rem;"></span>
                        </div>
                        <div x-show="open" x-collapse>
                            ${this.renderFieldsAndSubcategories(category)}
                        </div>
                    </div>
                `;
            });

            container.innerHTML = html;
        },

        renderFieldsAndSubcategories(category) {
            let html = '';

            // Render direct fields
            if (category.fields) {
                category.fields.forEach(field => {
                    html += this.renderField(field);
                });
            }

            // Render subcategories
            if (category.subcategories) {
                category.subcategories.forEach(sub => {
                    html += `
                        <div class="vb-data-category" style="margin-left:0.5rem;" x-data="{ open: false }">
                            <div class="vb-data-category-header" @click="open = !open">
                                <span class="material-symbols-outlined" style="font-size:0.875rem;">subdirectory_arrow_right</span>
                                <span class="vb-data-category-name">${sub.name}</span>
                            </div>
                            <div x-show="open" x-collapse>
                                ${this.renderFieldsAndSubcategories(sub)}
                            </div>
                        </div>
                    `;
                });
            }

            return html;
        },

        renderField(field) {
            const typeClass = field.is_array ? 'array' : '';
            return `
                <div class="vb-data-field" @click="insertDataField('${field.path}')" title="${field.description || ''}">
                    <span class="vb-data-field-name">${field.name}</span>
                    <span class="vb-data-field-type ${typeClass}">${field.data_type}</span>
                </div>
            `;
        },

        insertDataField(path) {
            const selected = this.editor.getSelected();
            if (selected) {
                // If component is selected and has a data binding trait, update it
                const trait = selected.getTrait('dataSource') || selected.getTrait('value') || selected.getTrait('items');
                if (trait) {
                    selected.set(trait.get('name'), path);
                }
            }
        },

        filterDataFields() {
            // Implement search filtering
            const query = this.dataSearch.toLowerCase();
            const fields = document.querySelectorAll('.vb-data-field');
            fields.forEach(field => {
                const name = field.querySelector('.vb-data-field-name')?.textContent?.toLowerCase() || '';
                field.style.display = name.includes(query) ? '' : 'none';
            });
        },

        openDataPicker(bindingType, callback) {
            this.showDataPicker = true;
            this.currentPickerCallback = callback;
            this.pickerSearch = '';
            this.renderPickerFields(bindingType);
        },

        closeDataPicker() {
            this.showDataPicker = false;
            this.currentPickerCallback = null;
        },

        renderPickerFields(bindingType) {
            const container = document.getElementById('picker-fields-container');
            if (!container || !this.dataRegistry) return;

            const allPaths = this.dataRegistry.all_paths || [];
            let html = '';

            allPaths.forEach(path => {
                const field = this.findField(path);
                if (!field) return;

                // Filter by binding type
                if (bindingType === 'array' && !field.is_array) return;
                if (bindingType === 'scalar' && field.is_array) return;

                html += `
                    <div class="vb-picker-field" onclick="window.selectPickerField('${path}')">
                        <div class="vb-picker-field-info">
                            <div class="vb-picker-field-name">${field.name}</div>
                            <div class="vb-picker-field-path">{{${path}}}</div>
                        </div>
                        <span class="vb-data-field-type ${field.is_array ? 'array' : ''}">${field.data_type}</span>
                    </div>
                `;
            });

            container.innerHTML = html || '<p style="color:#6b7280;text-align:center;padding:2rem;">No matching fields</p>';
        },

        findField(path) {
            // Search through categories to find field by path
            const search = (categories) => {
                for (const cat of categories) {
                    if (cat.fields) {
                        const found = cat.fields.find(f => f.path === path);
                        if (found) return found;
                    }
                    if (cat.subcategories) {
                        const found = search(cat.subcategories);
                        if (found) return found;
                    }
                }
                return null;
            };
            return search(this.dataRegistry.categories || []);
        },

        filterPickerFields() {
            const query = this.pickerSearch.toLowerCase();
            const fields = document.querySelectorAll('.vb-picker-field');
            fields.forEach(field => {
                const name = field.querySelector('.vb-picker-field-name')?.textContent?.toLowerCase() || '';
                const path = field.querySelector('.vb-picker-field-path')?.textContent?.toLowerCase() || '';
                field.style.display = (name.includes(query) || path.includes(query)) ? '' : 'none';
            });
        },

        openPreview() {
            const config = window.VISUAL_BUILDER_CONFIG;
            if (config.previewUrl && config.previewUrl !== '#') {
                window.open(config.previewUrl, '_blank');
            } else {
                alert('Please save the design first to preview it.');
            }
        },

        exportToCode() {
            const html = this.generateHTML();
            const css = this.generateCSS();

            // Copy to clipboard
            const code = `<!-- HTML -->\n${html}\n\n/* CSS */\n${css}`;
            navigator.clipboard.writeText(code).then(() => {
                alert('Code copied to clipboard! You can paste it in the code editor.');
            });
        },

        generateHTML() {
            let html = this.editor.getHtml();

            // Process data bindings
            const components = this.editor.getComponents();
            const processComponent = (component) => {
                const attrs = component.getAttributes();
                const dataSource = component.get('dataSource');
                const value = component.get('value');
                const items = component.get('items');

                // Handle array data sources
                if (dataSource && attrs['data-component'] === 'leaderboard') {
                    // Replace sample content with Handlebars loop
                    const listEl = component.find('.leaderboard-list')[0];
                    if (listEl) {
                        listEl.set('content', `
                            {{#each ${dataSource}}}
                            <div class="leaderboard-item rank-{{this.rank}}">
                                <div class="rank-badge">{{this.rank}}</div>
                                <span class="store-name">{{this.store_name}}</span>
                                <span class="store-value">{{this.value}}</span>
                            </div>
                            {{/each}}
                        `);
                    }
                }

                // Handle scalar value bindings
                if (value && attrs['data-component'] === 'stat-card') {
                    const valueEl = component.find('.stat-value')[0];
                    if (valueEl) {
                        valueEl.set('content', `{{${value}}}`);
                    }
                }

                // Process children
                component.get('components')?.forEach(processComponent);
            };

            components.forEach(processComponent);

            return this.editor.getHtml();
        },

        generateCSS() {
            return this.editor.getCss();
        },

        async saveDesign() {
            const config = window.VISUAL_BUILDER_CONFIG;

            // Generate code
            const html = this.generateHTML();
            const css = this.generateCSS();
            const projectData = this.editor.getProjectData();

            // Prepare form data
            document.getElementById('html-code-input').value = html;
            document.getElementById('css-code-input').value = css;
            document.getElementById('js-code-input').value = '';
            document.getElementById('visual-data-input').value = JSON.stringify(projectData);

            // Submit via fetch
            const formData = new FormData(document.getElementById('save-form'));
            formData.set('name', this.designName);

            try {
                const response = await fetch(config.saveUrl, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': config.csrfToken,
                    }
                });

                const result = await response.json();

                if (result.success) {
                    alert('Design saved successfully!');
                    if (result.redirect) {
                        window.location.href = result.redirect;
                    }
                } else {
                    alert('Error saving design: ' + (result.error || 'Unknown error'));
                }
            } catch (error) {
                console.error('Save error:', error);
                alert('Error saving design. Please try again.');
            }
        }
    };
}

// Global function for picker field selection (called from onclick)
window.selectPickerField = function(path) {
    const builder = Alpine.$data(document.querySelector('.visual-builder-container'));
    if (builder && builder.currentPickerCallback) {
        builder.currentPickerCallback(path);
        builder.closeDataPicker();
    }
};
