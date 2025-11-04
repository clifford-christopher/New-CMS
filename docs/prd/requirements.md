# Requirements

### Functional

- **FR1**: The system shall display a list of available news triggers/categories and allow users to select a trigger to configure
- **FR2**: The system shall accept stock ID input for testing and configuration purposes
- **FR3**: The system shall load existing configurations for a selected trigger, displaying current model, data APIs, and all three prompt types (paid, unpaid, crawler)
- **FR4**: The system shall display a list of data APIs currently configured for a trigger and allow users to add or remove APIs from a predefined list
- **FR5**: The system shall validate that required APIs are present in the configuration before allowing generation
- **FR6**: The system shall fetch data from configured APIs for a specified stock ID and display raw JSON responses in an organized, readable format
- **FR7**: The system shall show API call status indicators (success, failure, latency) for each data retrieval operation
- **FR8**: The system shall execute existing parser scripts to convert raw JSON data into structured format
- **FR9**: The system shall display structured data output with clear section labels and show the mapping between raw data and structured sections
- **FR10**: The system shall handle parser errors gracefully with clear, actionable error messages
- **FR11**: The system shall allow users to reorder data sections using drag-and-drop or numbered input
- **FR12**: The system shall preview how section order affects the final data structure passed to AI models
- **FR13**: The system shall provide a tabbed full-text prompt editor with syntax highlighting and real-time validation of data placeholder references for each prompt type (paid, unpaid, crawler)
- **FR14**: The system shall display the current prompt template for the selected tab with clear indication of data placeholders
- **FR15**: The system shall preview the final prompt with actual data substituted before generation for the selected prompt type
- **FR16**: The system shall provide version history and undo capability for prompt changes per prompt type
- **FR17**: The system shall display available LLM models and allow selection of multiple models for parallel testing
- **FR18**: The system shall display model-specific settings (temperature, max tokens) and show cost estimates for selected models
- **FR19**: The system shall generate news articles in parallel across selected models for checked prompt types only when triggered by user
- **FR20**: The system shall display real-time generation status indicators during news creation per prompt type
- **FR21**: The system shall display generated news grouped by prompt type, then by model for comparison
- **FR22**: The system shall show generation metadata including time, tokens used, and actual cost for each generation per prompt type per model
- **FR23**: The system shall allow inline editing of data or prompts after initial generation and support rapid regeneration for selected prompt types
- **FR24**: The system shall track generation history within a session and indicate what changed between iterations including which prompt types were tested
- **FR25**: The system shall provide a "Publish" function to save finalized configurations for all three prompt types with confirmation dialog showing what will be saved
- **FR26**: The system shall validate that all prompt type configurations are complete and tested before allowing publication
- **FR27**: The system shall save published configurations including all three prompt types to database with versioning
- **FR28**: The system shall set published configurations for all prompt types as active for automated news generation in production
- **FR29**: The system shall validate that stock IDs exist in the database before processing
- **FR30**: The system shall handle API failures gracefully (timeout, rate limits, invalid responses) with user-friendly error messages
- **FR31**: The system shall prevent publishing of incomplete or untested configurations
- **FR32**: The system shall log all configuration changes with user identity, timestamp, and change details
- **FR33**: The system shall track which configurations are currently live in production
- **FR34**: The system shall maintain history of prompt versions and model selections for audit purposes
- **FR35**: The system shall support three independent prompt types (paid, unpaid, crawler) per trigger with separate prompt templates
- **FR36**: The system shall display paid prompt type by default with checkboxes to enable unpaid and crawler prompt types
- **FR37**: The system shall share data configuration, section management, and model selection across all prompt types
- **FR38**: The system shall provide a tabbed interface for editing prompts, allowing users to switch between paid, unpaid, and crawler prompt types
- **FR39**: The system shall generate news only for checked/selected prompt types
- **FR40**: The system shall display actual token usage, generation time, and cost per model per prompt type after generation completes

### Non Functional

- **NFR1**: The system shall load pages in under 2 seconds for optimal user experience
- **NFR2**: Data API fetching shall complete within 5 seconds per API call
- **NFR3**: News generation responses shall be delivered within 30 seconds (model dependent)
- **NFR4**: The system shall support 5-10 concurrent user sessions without degradation
- **NFR5**: The system shall be compatible with modern browsers (Chrome, Firefox, Safari, Edge) - last 2 versions
- **NFR6**: The system shall provide a responsive design optimized for desktop with tablet support
- **NFR7**: The system shall securely store API keys for LLM services with encryption
- **NFR8**: The system shall implement input validation to prevent injection attacks
- **NFR9**: The system shall implement rate limiting to prevent abuse and control costs
- **NFR10**: The system shall track LLM API costs and implement spending limits to prevent budget overruns
- **NFR11**: The system shall maintain backwards compatibility with existing news generation system during transition
- **NFR12**: The system shall respect LLM API rate limits and quotas
- **NFR13**: Published configurations shall generate production-quality news with less than 5% error rate
- **NFR14**: The system shall enable configuration creation from trigger selection to publication in under 2 hours
- **NFR15**: The system shall maintain comprehensive audit logs for compliance purposes
