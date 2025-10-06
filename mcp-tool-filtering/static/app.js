function demoApp() {
    return {
        // State
        currentQuery: "",
        isRunning: false,
        speed: 'real',
        showToolAnimation: false,
        metricsAnimating: false,
        totalTools: 0,  // Will be loaded from API
        showSettings: false,
        showFilteringModal: false,
        showAllTools: false,
        showConnectedTools: false,  // New state for connected tools modal
        showOverlay: true,  // Start with overlay visible
        overlayQuery: "",   // Separate query for overlay

        // Demo queries - Optimized to showcase tool confusion without Redis filtering
        demoQueries: {
            query1: 'Search customer support tickets with "payment processing" errors',
            query2: "Summarize todays logs from the Payment Service. Are there any irregularities?",
            query3: "Search our customer facing documentation to find ways for the to manually enter payment details",
            query4: "Create a high priority incident regarding a payment service outage"
        },

        // All available tools - will be loaded from API
        allTools: [],

        // Panel states - initialized with zeros, will be populated from API
        baseline: {
            toolCount: 0,
            tokens: 0,
            latency: '0',
            cost: 0,
            progress: 0,
            isRunning: false,
            response: '',
            toolsUsed: []
        },

        optimized: {
            toolCount: 0,
            tokens: 0,
            latency: '0',
            cost: 0,
            progress: 0,
            isRunning: false,
            response: '',
            cacheStatus: 'MISS',
            similarity: null,
            vectorSearchTime: 0,
            selectedTools: [],
            toolsUsed: [],
            filteredTools: []
        },

        // Metrics - calculated from actual results
        metrics: {
            totalQueries: 0,
            avgLatencyReduction: 0,
            avgTokenReduction: 0,
            totalCostSavings: 0,
            cacheHitRate: 0,
            avgVectorSearchTime: 0,
            latencyHistory: [],
            tokenHistory: []
        },

        // Cache stats
        cacheStats: {
            totalItems: 0,
            avgTTL: 300,
            storageSize: '0KB',
            items: []
        },

        // Query history for cache simulation
        queryHistory: [],

        // Initialize
        async init() {
            console.log('Demo app initializing...');
            try {
                await this.loadTools();
                console.log(`Loaded ${this.totalTools} tools`);
                this.resetDemo();
                this.loadCacheStats();
                console.log('Demo app initialized successfully');
            } catch (error) {
                console.error('Demo app initialization failed:', error);
            }
        },

        // Load tools from API
        async loadTools() {
            try {
                const response = await fetch('/api/tools');
                this.allTools = await response.json();
                this.totalTools = this.allTools.length;
                console.log(`Loaded ${this.totalTools} tools from API`);
            } catch (error) {
                console.error('Failed to load tools:', error);
                this.totalTools = 84;  // Fallback
            }
        },

        // Execute query from overlay
        async executeOverlayQuery() {
            if (this.isRunning || !this.overlayQuery.trim()) {
                return;
            }
            
            // Copy overlay query to main query
            this.currentQuery = this.overlayQuery;
            
            // Slide overlay down with animation
            this.showOverlay = false;
            
            // Wait for animation then execute
            setTimeout(() => {
                this.executeQuery();
            }, 300);
        },

        // Query execution - REAL API CALLS
        async executeQuery() {
            console.log('executeQuery called with:', this.currentQuery);
            
            if (this.isRunning) {
                console.log('Already running, skipping');
                return;
            }
            if (!this.currentQuery.trim()) {
                console.log('Empty query, skipping');
                return;
            }
            
            console.log('Starting query execution...');
            this.isRunning = true;
            this.resetPanels();
            this.showToolAnimation = true;
            
            // Make real API calls to both endpoints simultaneously
            const baselinePromise = this.runBaseline();
            const optimizedPromise = this.runOptimized();

            await Promise.all([baselinePromise, optimizedPromise]);

            this.isRunning = false;
            this.updateMetrics();
            this.queryHistory.push({
                query: this.currentQuery,
                timestamp: new Date(),
                baseline: { ...this.baseline },
                optimized: { ...this.optimized }
            });
            
            // Keep the query visible so user can see what they asked

            setTimeout(() => {
                this.showToolAnimation = false;
            }, 2000);
        },

        async runBaseline() {
            this.baseline.isRunning = true;
            this.baseline.progress = 20;
            
            try {
                // Make real API call with timeout
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
                
                const response = await fetch('/api/query', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        query: this.currentQuery,
                        panel: 'baseline'
                    }),
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);
                
                if (!response.ok) {
                    throw new Error(`API call failed: ${response.status} ${response.statusText}`);
                }
                
                const data = await response.json();
                console.log('Baseline API response:', data);
                
                // Update with real data from API
                this.baseline.toolCount = data.tools_count || this.totalTools;
                this.baseline.tokens = data.tokens || 0;
                this.baseline.latency = data.latency ? data.latency.toFixed(3) : '0';
                this.baseline.cost = data.cost || 0;
                this.baseline.response = data.response || '';
                this.baseline.toolsUsed = data.tools_used || [];
                
                // Show tool execution for baseline (always executes tools)
                this.showToolExecution('baseline', this.baseline.toolsUsed);
                
            } catch (error) {
                console.error('Baseline API call failed:', error);
                this.updateToolList('baselineToolList', [], true);
                // Set default values on error
                this.baseline.toolCount = 84;
                this.baseline.tokens = 0;
                this.baseline.latency = '0';
                this.baseline.cost = 0;
            }
            
            this.baseline.progress = 100;
            this.baseline.isRunning = false;
        },

        async runOptimized() {
            this.optimized.isRunning = true;
            this.optimized.progress = 20;
            
            try {
                // Make real API call with timeout
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
                
                const response = await fetch('/api/query', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        query: this.currentQuery,
                        panel: 'optimized'
                    }),
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);
                
                if (!response.ok) {
                    throw new Error(`API call failed: ${response.status} ${response.statusText}`);
                }
                
                const data = await response.json();
                console.log('Optimized API response:', data);
                
                // Update with real data from API
                this.optimized.toolCount = data.tools_count || 0;
                this.optimized.tokens = data.tokens || 0;
                this.optimized.latency = data.latency ? data.latency.toFixed(3) : '0';
                this.optimized.cost = data.cost || 0;
                this.optimized.response = data.response || '';
                this.optimized.cacheStatus = data.cache_status || 'MISS';
                this.optimized.similarity = data.similarity || null;
                this.optimized.vectorSearchTime = data.vector_search_time || 0;
                this.optimized.toolsUsed = data.tools_used || [];
                this.optimized.filteredTools = data.filtered_tools || [];
                
                // Update cache stats if cache hit
                if (data.cache_status === 'HIT') {
                    this.cacheStats.totalItems = (this.cacheStats.totalItems || 0) + 1;
                }
                
                // Handle cache hit vs tool execution
                if (this.optimized.cacheStatus === 'HIT') {
                    this.showCacheHit(data.similarity);
                } else {
                    this.showToolExecution('optimized', this.optimized.toolsUsed);
                }
                
            } catch (error) {
                console.error('Optimized API call failed:', error);
                this.updateToolList('optimizedToolList', [], true);
                // Set default values on error
                this.optimized.toolCount = 3;
                this.optimized.tokens = 0;
                this.optimized.latency = '0';
                this.optimized.cost = 0;
            }
            
            this.optimized.progress = 100;
            this.optimized.isRunning = false;
        },

        updateMetrics() {
            this.metricsAnimating = true;
            
            this.metrics.totalQueries += 1;
            
            // Calculate actual reductions from real data
            const latencyReduction = this.baseline.latency > 0 
                ? ((parseFloat(this.baseline.latency) - parseFloat(this.optimized.latency)) / parseFloat(this.baseline.latency)) * 100
                : 0;
            const tokenReduction = this.baseline.tokens > 0
                ? ((this.baseline.tokens - this.optimized.tokens) / this.baseline.tokens) * 100
                : 0;
            const costSavings = this.baseline.cost - this.optimized.cost;
            
            // Store history for averaging
            this.metrics.latencyHistory.push(latencyReduction);
            this.metrics.tokenHistory.push(tokenReduction);
            
            // Calculate running averages from actual data
            this.metrics.avgLatencyReduction = Math.round(
                this.metrics.latencyHistory.reduce((a, b) => a + b, 0) / this.metrics.latencyHistory.length
            );
            this.metrics.avgTokenReduction = Math.round(
                this.metrics.tokenHistory.reduce((a, b) => a + b, 0) / this.metrics.tokenHistory.length
            );
            this.metrics.totalCostSavings += costSavings;
            
            // Calculate cache hit rate from history
            const cacheHits = this.queryHistory.filter(q => q.optimized && q.optimized.cacheStatus === 'HIT').length;
            this.metrics.cacheHitRate = this.queryHistory.length > 0 
                ? Math.round((cacheHits / this.queryHistory.length) * 100)
                : 0;
            
            // Calculate average vector search time
            const vectorTimes = this.queryHistory
                .filter(q => q.optimized && q.optimized.vectorSearchTime)
                .map(q => q.optimized.vectorSearchTime);
            this.metrics.avgVectorSearchTime = vectorTimes.length > 0
                ? Math.round(vectorTimes.reduce((a, b) => a + b, 0) / vectorTimes.length)
                : 0;
            
            setTimeout(() => {
                this.metricsAnimating = false;
            }, 500);
        },

        // Demo controls
        setQuery(query) {
            this.currentQuery = query;
        },

        async runFullScenario() {
            const queries = [
                this.demoQueries.query1,
                this.demoQueries.query2,
                this.demoQueries.query3,
                this.demoQueries.query4
            ];

            for (let i = 0; i < queries.length; i++) {
                this.currentQuery = queries[i];
                await this.executeQuery();
                
                if (i < queries.length - 1) {
                    await this.delay(this.speed === 'fast' ? 500 : 2000);
                }
            }
        },

        resetDemo() {
            this.queryHistory = [];
            this.metrics = {
                totalQueries: 0,
                avgLatencyReduction: 0,
                avgTokenReduction: 0,
                totalCostSavings: 0,
                cacheHitRate: 0,
                avgVectorSearchTime: 0,
                latencyHistory: [],
                tokenHistory: []
            };
            this.resetPanels();
            this.clearCache();
        },


        async clearCache() {
            try {
                await fetch('/api/cache', { method: 'DELETE' });
                this.cacheStats = {
                    totalItems: 0,
                    avgTTL: 300,
                    storageSize: '0KB',
                    items: []
                };
            } catch (error) {
                console.error('Failed to clear cache:', error);
            }
        },

        loadCacheStats() {
            // Cache stats tracked locally from API responses
            const cacheHits = this.queryHistory.filter(q => 
                q.optimized && q.optimized.cacheStatus === 'HIT'
            ).length;
            this.cacheStats.totalItems = cacheHits;
        },

        // Get logo path for server
        getServerLogo(serverName) {
            if (!serverName) return null;
            const server = serverName.toLowerCase();
            const logoMap = {
                'confluence': '/logos/confluence.png',
                'datadog': '/logos/datadog.svg',
                'jira': '/logos/jira.svg',
                'm365': '/logos/m365.png',
                'microsoft': '/logos/m365.png',
                'office365': '/logos/m365.png',
                'pagerduty': '/logos/pagerduty.png',
                'snowflake': '/logos/snowflake.png',
                'zendesk': '/logos/zendesk.png',
            };
            return logoMap[server] || null;
        },

        // Get server name from tool name
        getServerFromTool(toolName) {
            if (!toolName || !this.allTools) return 'unknown';
            const toolDetails = this.allTools.find(t => t.name === toolName);
            return toolDetails ? toolDetails.server : 'unknown';
        },

        // Get logo path from tool name
        getServerLogoFromTool(toolName) {
            const server = this.getServerFromTool(toolName);
            return this.getServerLogo(server);
        },

        // Tool list display
        updateToolList(containerId, tools, isError = false) {
            console.log(`updateToolList called: containerId=${containerId}, tools=`, tools, `isError=${isError}`);
            const container = document.getElementById(containerId);
            if (!container) {
                console.error(`Container not found: ${containerId}`);
                return;
            }
            
            if (isError) {
                container.innerHTML = '<div class="text-red-500 text-sm">Error loading tools</div>';
                return;
            }
            
            if (!tools || tools.length === 0) {
                container.innerHTML = '<div class="text-gray-500 text-sm">No tools selected</div>';
                return;
            }
            
            const toolsHtml = tools.slice(0, 10).map(toolName => {
                // Find tool details from allTools
                const toolDetails = this.allTools.find(t => t.name === toolName);
                const server = toolDetails ? toolDetails.server : 'unknown';
                const type = toolDetails ? toolDetails.type : 'unknown';
                const logoPath = this.getServerLogo(server);
                
                return `
                    <div class="tool-item">
                        <div class="flex items-center justify-between mb-2">
                            <div class="flex items-center gap-2">
                                ${logoPath ? 
                                    `<img src="${logoPath}" alt="${server}" class="w-4 h-4 flex-shrink-0" onerror="this.style.display='none'; this.nextElementSibling.style.display='block'"><div class="w-2 h-2 bg-blue-400 rounded-full" style="display:none"></div>` : 
                                    `<div class="w-2 h-2 bg-blue-400 rounded-full"></div>`
                                }
                                <div class="font-semibold text-sm text-gray-800">${toolName}</div>
                            </div>
                            <div class="text-xs font-medium text-gray-500 bg-gray-100 px-2 py-1 rounded-full uppercase tracking-wide">${server}</div>
                        </div>
                        <div class="flex items-center gap-1 text-xs text-gray-600">
                            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                            </svg>
                            <span class="capitalize">${type} operation</span>
                        </div>
                    </div>
                `;
            }).join('');
            
            container.innerHTML = toolsHtml;
            
            // Show count if more tools exist
            if (tools.length > 10) {
                container.innerHTML += `<div class="text-xs text-gray-500 text-center mt-2">+ ${tools.length - 10} more tools</div>`;
            }
        },
        
        // Show query in both panels
        // Query is now displayed statically in the left panel
        
        // Show cache hit with similarity score
        showCacheHit(similarity) {
            // Show cache hit section
            const cacheHit = document.getElementById('optimizedCacheHit');
            const similaritySpan = document.getElementById('optimizedSimilarityScore');
            
            if (cacheHit && similaritySpan) {
                similaritySpan.textContent = similarity || 'N/A';
                cacheHit.style.display = 'block';
            }
        },
        
        // Show tool execution with selected tools
        showToolExecution(panel, tools) {
            const panelPrefix = panel === 'baseline' ? 'baseline' : 'optimized';
            
            // Hide cache hit section for optimized panel when showing tools
            if (panel === 'optimized') {
                const cacheHit = document.getElementById('optimizedCacheHit');
                if (cacheHit) cacheHit.style.display = 'none';
            }
            
            // Update tool list with animation (tool execution sections are always visible in new layout)
            this.updateToolList(`${panelPrefix}ToolList`, tools);
            
            // Add shimmer effect to performance metrics when data updates
            if (tools && tools.length > 0) {
                this.animateMetrics(panelPrefix);
            }
        },
        
        resetPanels() {
            this.baseline = {
                toolCount: 0,
                tokens: 0,
                latency: '0',
                cost: 0,
                progress: 0,
                isRunning: false,
                response: '',
                toolsUsed: []
            };

            this.optimized = {
                toolCount: 0,
                tokens: 0,
                latency: '0',
                cost: 0,
                progress: 0,
                isRunning: false,
                response: '',
                cacheStatus: 'MISS',
                similarity: null,
                vectorSearchTime: 0,
                selectedTools: [],
                toolsUsed: [],
                filteredTools: []
            };
            
            // Clear tool lists
            this.updateToolList('baselineToolList', []);
            this.updateToolList('optimizedToolList', []);
            
            // Hide cache hit display
            const optimizedCacheHit = document.getElementById('optimizedCacheHit');
            if (optimizedCacheHit) optimizedCacheHit.style.display = 'none';
        },

        // Animation helpers
        animateMetrics(panelPrefix) {
            // Animate metric cards with a subtle highlight
            const metrics = document.querySelectorAll(`#${panelPrefix} .metric-card, .comparison-highlight`);
            metrics.forEach((card, index) => {
                setTimeout(() => {
                    card.classList.add('animate');
                    setTimeout(() => card.classList.remove('animate'), 600);
                }, index * 100);
            });
        },

        // Modal functions
        showSmartFilteringModal() {
            console.log('showSmartFilteringModal called');
            console.log('optimized.toolsUsed:', this.optimized.toolsUsed);
            console.log('optimized.filteredTools:', this.optimized.filteredTools);
            console.log('optimized.cacheStatus:', this.optimized.cacheStatus);
            console.log('showFilteringModal current state:', this.showFilteringModal);
            
            // Only show modal if there are filtered tools to display
            if (this.optimized.filteredTools && this.optimized.filteredTools.length > 0) {
                console.log('Showing modal...');
                this.showFilteringModal = true;
                console.log('showFilteringModal new state:', this.showFilteringModal);
            } else {
                console.log('No filtered tools to display in modal');
            }
        },

        closeModal() {
            this.showFilteringModal = false;
        },

        showSemanticCacheInfo() {
            // For now, just log - could show tooltip or info modal later
            console.log('Semantic cache info requested');
        },

        showQueryOverlay() {
            this.showOverlay = true;
            this.overlayQuery = this.currentQuery || "";
        },

        showAllToolsModal() {
            this.showAllTools = true;
        },
        
        showConnectedToolsModal() {
            this.showConnectedTools = true;
        },

        getAllToolsByServerHtml() {
            if (!this.allTools || this.allTools.length === 0) {
                return '<div class="text-gray-500 text-sm">Loading tools...</div>';
            }

            // Group tools by server
            const toolsByServer = {};
            this.allTools.forEach(tool => {
                const server = tool.server || 'Unknown';
                if (!toolsByServer[server]) {
                    toolsByServer[server] = [];
                }
                toolsByServer[server].push(tool);
            });

            // Sort servers alphabetically
            const sortedServers = Object.keys(toolsByServer).sort();

            // Generate HTML for each server group
            return sortedServers.map(server => {
                const tools = toolsByServer[server];
                const logoPath = this.getServerLogo(server);
                const toolsHtml = tools.map(tool => `
                    <div class="bg-gray-50 rounded-lg p-3 hover:bg-gray-100 transition-colors">
                        <div class="flex items-center justify-between mb-1">
                            <div class="font-medium text-sm text-gray-800">${tool.name}</div>
                            <div class="text-xs text-gray-500 capitalize">${tool.type || 'unknown'}</div>
                        </div>
                        ${tool.description ? `<div class="text-xs text-gray-600">${tool.description}</div>` : ''}
                    </div>
                `).join('');

                return `
                    <div class="border border-gray-200 rounded-lg overflow-hidden">
                        <div class="bg-gradient-to-r from-gray-50 to-gray-100 px-4 py-3 border-b border-gray-200">
                            <div class="flex items-center justify-between">
                                <div class="flex items-center gap-2">
                                    ${logoPath ? 
                                        `<img src="${logoPath}" alt="${server}" class="w-5 h-5 flex-shrink-0" onerror="this.style.display='none'">` : 
                                        ''
                                    }
                                    <h4 class="font-semibold text-gray-800">${server}</h4>
                                </div>
                                <span class="text-xs font-medium text-gray-500 bg-white px-2 py-1 rounded-full">${tools.length} tools</span>
                            </div>
                        </div>
                        <div class="p-4 space-y-2">
                            ${toolsHtml}
                        </div>
                    </div>
                `;
            }).join('');
        },
        
        getConnectedToolsHtml() {
            if (!this.allTools || this.allTools.length === 0) {
                return '<div class="text-gray-500 text-sm">Loading tools...</div>';
            }

            // Group tools by server
            const toolsByServer = {};
            this.allTools.forEach(tool => {
                const server = tool.server || 'Unknown';
                if (!toolsByServer[server]) {
                    toolsByServer[server] = [];
                }
                toolsByServer[server].push(tool);
            });

            // Sort servers alphabetically
            const sortedServers = Object.keys(toolsByServer).sort();

            // Generate HTML for each server group with green connection indicators
            return sortedServers.map(server => {
                const tools = toolsByServer[server];
                const logoPath = this.getServerLogo(server);
                const toolsHtml = tools.map(tool => `
                    <div class="bg-gray-50 rounded-lg p-3 hover:bg-gray-100 transition-colors">
                        <div class="flex items-center justify-between mb-1">
                            <div class="flex items-center gap-2">
                                <div class="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                                <div class="font-medium text-sm text-gray-800">${tool.name}</div>
                            </div>
                            <div class="text-xs text-gray-500 capitalize">${tool.type || 'unknown'}</div>
                        </div>
                        ${tool.description ? `<div class="text-xs text-gray-600 ml-3.5">${tool.description}</div>` : ''}
                    </div>
                `).join('');

                return `
                    <div class="border border-gray-200 rounded-lg overflow-hidden">
                        <div class="bg-gradient-to-r from-gray-50 to-gray-100 px-4 py-3 border-b border-gray-200">
                            <div class="flex items-center justify-between">
                                <div class="flex items-center gap-2">
                                    <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                                    ${logoPath ? 
                                        `<img src="${logoPath}" alt="${server}" class="w-5 h-5 flex-shrink-0" onerror="this.style.display='none'">` : 
                                        ''
                                    }
                                    <h4 class="font-semibold text-gray-800">${server}</h4>
                                    <span class="text-xs text-green-600 font-medium">Connected</span>
                                </div>
                                <span class="text-xs font-medium text-gray-500 bg-white px-2 py-1 rounded-full">${tools.length} tools</span>
                            </div>
                        </div>
                        <div class="p-4 space-y-2">
                            ${toolsHtml}
                        </div>
                    </div>
                `;
            }).join('');
        },

        getFilteredToolsHtml() {
            if (!this.optimized.filteredTools || this.optimized.filteredTools.length === 0) {
                return '<div class="text-gray-500 text-sm">No tools available</div>';
            }

            return this.optimized.filteredTools.slice(0, 3).map(toolName => {
                const toolDetails = this.allTools.find(t => t.name === toolName);
                const server = toolDetails ? toolDetails.server : 'unknown';
                const type = toolDetails ? toolDetails.type : 'unknown';
                const logoPath = this.getServerLogo(server);
                
                return `
                    <div class="border border-gray-200 rounded-lg p-3 bg-white hover:bg-gray-50 transition-colors">
                        <div class="flex items-center justify-between mb-2">
                            <div class="flex items-center gap-2">
                                ${logoPath ? 
                                    `<img src="${logoPath}" alt="${server}" class="w-4 h-4 flex-shrink-0" onerror="this.style.display='none'; this.nextElementSibling.style.display='block'"><div class="w-2 h-2 bg-blue-400 rounded-full" style="display:none"></div>` : 
                                    `<div class="w-2 h-2 bg-blue-400 rounded-full"></div>`
                                }
                                <div class="font-semibold text-sm text-gray-800">${toolName}</div>
                            </div>
                            <div class="text-xs font-medium text-gray-500 bg-gray-100 px-2 py-1 rounded-full uppercase tracking-wide">${server}</div>
                        </div>
                        <div class="flex items-center gap-1 text-xs text-gray-600">
                            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                            </svg>
                            <span class="capitalize">${type} operation</span>
                        </div>
                    </div>
                `;
            }).join('');
        },

        // Utility functions
        delay(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }
    };
}