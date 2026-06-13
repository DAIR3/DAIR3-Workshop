"""
cls_foo.py
Multi-Agent Orchestration class for distributing messages and managing agent interactions.
Handles vulnerability analysis, judgment, and reflection workflows.
Now includes blockchain integrity verification for conversation logs.

By Juan B. Gutiérrez, Professor of Mathematics 
University of Texas at San Antonio.

License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
"""

import os
import json
import sys
from datetime import datetime
from cls_openai import OpenAIAgent
from cls_anthropic import AnthropicAgent
from cls_blockchain import IntegrityManager
from md_loader import load_persona, read_md_file
from cls_provider_catalog import resolve_legacy_model, engine_class_for


class MultiAgentOrchestrator:
    """
    Orchestrates multiple AI agents (OpenAI and Anthropic) for collaborative analysis.
    Manages message distribution, vulnerability analysis, judgment, and reflection workflows.
    Now includes blockchain integrity verification for all conversations.
    """
    
    def __init__(self, config_file="config.json"):
        """Initialize the multi-agent system from configuration file"""
        self.agents = []
        self.active_agents_working = 0
        self.config_file = config_file
        
        # Load configuration
        try:
            with open(config_file, "r") as f:
                config_data = json.load(f)
        except FileNotFoundError:
            print(f"Config file {config_file} not found, trying default config.json")
            with open("config.json", "r") as f:
                config_data = json.load(f)
        
        self.config = config_data["CONFIG"]
        self.models = config_data["MODELS"]
        self.user = self.config["user"]
        
        # Get or create blockchain salt from config
        if "blockchain_salt" not in self.config:
            # Generate new salt and save to config
            import hashlib
            import time
            timestamp = str(time.time())
            new_salt = hashlib.sha256(f"multi_agent_system_{timestamp}".encode()).hexdigest()[:16]
            self.config["blockchain_salt"] = new_salt
            
            # Save the updated config
            config_data["CONFIG"] = self.config
            try:
                with open(config_file, "w") as f:
                    json.dump(config_data, f, indent=4)
                print(f"Generated and saved new blockchain salt: {new_salt}")
            except Exception as e:
                print(f"Warning: Could not save blockchain salt to config: {e}")
        
        # Initialize blockchain integrity manager with global salt
        self.integrity_manager = IntegrityManager(global_salt=self.config.get("blockchain_salt"))
        
        # Initialize agents based on configuration
        self._initialize_agents()
        
        # Verify integrity of all loaded conversations
        self._verify_all_agent_integrity()
    
    def _initialize_agents(self):
        """Initialize all agents from configuration"""
        common_md = self.config.get("common_md", "common.md")
        for entry in self.models:
            # Prefer the new schema (cd_model + cd_provider). Fall back to the
            # legacy `model_code` field and the catalog's prefix-based detector
            # so old config.json files continue to work without migration.
            model_code = entry.get("cd_model") or entry.get("model_code")
            provider_code = entry.get("cd_provider")
            if not provider_code:
                provider_code, _ = resolve_legacy_model(model_code)
            agent_name = entry["agent_name"]
            harmonizer = bool(entry.get("harmonizer", False)) if isinstance(entry.get("harmonizer", False), bool) else str(entry.get("harmonizer", "false")).lower() == "true"

            # Build per-agent instructions from common.md + role .md with variable substitution.
            role_md = entry.get("instructions_file", "general.md")
            agent_instructions = load_persona(common_md, role_md, {
                "user": self.user,
                "name": agent_name,
            })

            try:
                AgentClass = engine_class_for(provider_code)
                agent = AgentClass(
                    model=model_code,
                    name=agent_name,
                    instructions=agent_instructions,
                    user=self.user,
                    config=self.config,
                    model_entry=entry,
                )

                # Stash persona source files + the raw model entry so the GUI
                # can switch roles at runtime and display the friendly model name.
                # _provider_code lets the GUI seed the Provider dropdown without
                # re-guessing from the class name.
                agent.common_md = common_md
                agent.role_md = role_md
                agent.model_entry = entry
                agent._provider_code = provider_code

                # Add harmonizer flag
                agent.harmonizer = harmonizer

                # Store harmonizer directive (from file or inline) if this is a harmonizer agent.
                # The directive contains a {source_agent_name} placeholder that the orchestrator
                # substitutes at judgment time, so we DO NOT pre-substitute it here.
                if harmonizer:
                    directive_file = entry.get("harmonizer_directive_file", "")
                    if directive_file:
                        agent.harmonizer_directive = read_md_file(directive_file)
                    elif "harmonizer_directive" in entry:
                        agent.harmonizer_directive = entry["harmonizer_directive"]
                
                # Initialize blockchain for this agent if conversation history exists
                if hasattr(agent, 'history_data') and agent.history_data.get('history'):
                    self._migrate_agent_to_blockchain(agent)
                
                self.agents.append(agent)
                print(f"Initialized agent: {agent_name} ({provider_code}/{model_code})")
                
            except Exception as e:
                print(f"Failed to initialize agent {agent_name}: {e}")            
    
    def _migrate_agent_to_blockchain(self, agent):
        """Migrate existing agent history to blockchain format if needed"""
        try:
            history = agent.history_data.get('history', [])
            if not history:
                return
            
            # Check if history already has blockchain data
            has_blockchain = any('blockchain' in entry for entry in history if isinstance(entry, dict))
            
            if not has_blockchain:
                print(f"Migrating {agent.name} conversation to blockchain format...")
                
                # Migrate history to include blockchain data
                migrated_history = self.integrity_manager.migrate_existing_history(agent.name, history)
                
                # Update agent's history
                agent.history_data['history'] = migrated_history
                if hasattr(agent, 'display_history'):
                    agent.display_history = migrated_history
                
                # Add blockchain metadata to agent's history file
                agent.history_data['blockchain_metadata'] = self.integrity_manager.get_or_create_blockchain(agent.name).get_chain_metadata(migrated_history)
                
                # Save the migrated conversation
                agent.save_conversation()
                print(f"Successfully migrated {agent.name} to blockchain format")
            
        except Exception as e:
            print(f"Error migrating {agent.name} to blockchain: {e}")
    
    def _verify_all_agent_integrity(self):
        """Verify blockchain integrity for all agents on startup"""
        print("Verifying conversation integrity for all agents...")
        
        for agent in self.agents:
            try:
                if hasattr(agent, 'history_data') and agent.history_data.get('history'):
                    history = agent.history_data['history']
                    is_valid, errors = self.integrity_manager.verify_agent_integrity(agent.name, history)
                    
                    if not is_valid:
                        print(f"⚠️  INTEGRITY WARNING for {agent.name}:")
                        for error in errors:
                            print(f"   - {error}")
                        
                        # Mark integrity issues in agent
                        agent.integrity_issues = errors
                        agent.integrity_valid = False
                    else:
                        print(f"✅ {agent.name}: Conversation integrity verified")
                        agent.integrity_issues = []
                        agent.integrity_valid = True
                        
            except Exception as e:
                print(f"Error verifying integrity for {agent.name}: {e}")
                agent.integrity_issues = [f"Verification error: {e}"]
                agent.integrity_valid = False
    
    def get_active_agents(self):
        """Get list of active agents"""
        return [agent for agent in self.agents if agent.active]
    
    def get_harmonizer_agents(self):
        """Get list of active harmonizer agents"""
        return [agent for agent in self.agents if agent.active and getattr(agent, 'harmonizer', False)]
    
    def get_non_harmonizer_agents(self):
        """Get list of active non-harmonizer agents"""
        return [agent for agent in self.agents if agent.active and not getattr(agent, 'harmonizer', False)]
    
    def send_message_with_integrity(self, agent, message):
        """
        Send message to agent with blockchain integrity tracking.
        This replaces direct calls to agent.send_message() in the workflow.
        """
        try:
            # Get current timestamp
            timestamp = datetime.now().isoformat()
            
            # Get current history
            history = agent.history_data.get('history', [])
            
            # Add user message with blockchain integrity
            user_entry = self.integrity_manager.add_message_with_integrity(
                agent.name, "user", message, timestamp, history
            )
            
            # Add to agent's history
            history.append(user_entry)
            agent.history_data['history'] = history
            if hasattr(agent, 'display_history'):
                agent.display_history = history
            
            # Send to agent (this will return the response)
            response = agent.send_message(message)
            
            # Now add the assistant response with blockchain integrity
            response_timestamp = datetime.now().isoformat()
            assistant_entry = self.integrity_manager.add_message_with_integrity(
                agent.name, "assistant", response, response_timestamp, history
            )
            
            # Add assistant response to history
            history.append(assistant_entry)
            agent.history_data['history'] = history
            if hasattr(agent, 'display_history'):
                agent.display_history = history
            
            # Update blockchain metadata and save conversation
            blockchain = self.integrity_manager.get_or_create_blockchain(agent.name)
            agent.history_data['blockchain_metadata'] = blockchain.get_chain_metadata(history)
            agent.save_conversation()
            
            return response
            
        except Exception as e:
            print(f"Error in send_message_with_integrity for {agent.name}: {e}")
            # Fallback to regular send_message
            return agent.send_message(message)
    
    def broadcast_message(self, message):
        """
        Broadcast a message to all active agents with blockchain integrity.
        Returns a dictionary with agent names as keys and responses as values.
        """
        responses = {}
        active_agents = self.get_active_agents()
        
        print(f"Broadcasting message to {len(active_agents)} active agents: '{message}'")
        
        for agent in active_agents:
            try:
                response = self.send_message_with_integrity(agent, message)
                responses[agent.name] = response
                print(f"Response from {agent.name}: {response[:100]}..." if len(response) > 100 else f"Response from {agent.name}: {response}")
            except Exception as e:
                error_msg = f"Error: {e}"
                responses[agent.name] = error_msg
                print(f"Error from {agent.name}: {error_msg}")
        
        return responses

    def send_message_to_agent(self, agent_name, message):
        """Send a message to a specific agent by name with blockchain integrity."""
        agent = self.get_agent_by_name(agent_name)
        if not agent:
            return f"Error: Agent '{agent_name}' not found"
        
        if not agent.active:
            return f"Error: Agent '{agent_name}' is not active"
        
        try:
            return self.send_message_with_integrity(agent, message)
        except Exception as e:
            return f"Error sending message to {agent_name}: {e}"
    
    def send_vulnerability_analysis(self, source_agent_name):
        """
        Send vulnerability analysis request to other agents about source agent's latest response.
        Now uses blockchain-verified messaging.
        """
        source_agent = None
        for agent in self.agents:
            if agent.name == source_agent_name:
                source_agent = agent
                break
        
        if not source_agent or not source_agent.latest_response:
            print(f"No response found for agent {source_agent_name}")
            return {}
        
        message = f"Agent {source_agent_name} answered the same question as follows, find flaws: {source_agent.latest_response}"
        
        # Send to all other active agents with blockchain integrity
        responses = {}
        for agent in self.get_active_agents():
            if agent.name != source_agent_name:
                try:
                    response = self.send_message_with_integrity(agent, message)
                    responses[agent.name] = response
                except Exception as e:
                    responses[agent.name] = f"Error: {e}"
        
        return responses
    
    def send_judgment_analysis(self, source_agent_name):
        """
        Send judgment analysis to harmonizer agents with blockchain integrity.
        Uses custom harmonizer_directive from config if available.
        Returns: tuple of (responses_dict, messages_dict) where messages_dict contains what was sent to each agent
        """
        # Collect responses from non-harmonizer agents
        summary_map = {}
        for agent in self.get_non_harmonizer_agents():
            if agent.latest_response:
                summary_map[agent.name] = agent.latest_response
        
        if not summary_map:
            print("No responses found from non-harmonizer agents")
            return {}, {}
        
        # Build composite text once (shared by all harmonizers)
        composite = []
        for agent_name, response in summary_map.items():
            composite.append(f"\n \n Agent {agent_name}: {response}")
        composite_text = "".join(composite)
        
        # Send to harmonizer agents with blockchain integrity
        responses = {}
        messages = {}  # Track what message was sent to each agent
        
        for agent in self.get_harmonizer_agents():
            # Use agent's custom harmonizer directive if available, otherwise use default
            if hasattr(agent, 'harmonizer_directive') and agent.harmonizer_directive:
                # Replace {source_agent_name} placeholder with actual agent name
                directive = agent.harmonizer_directive.replace("{source_agent_name}", source_agent_name)
                message = f"{directive} \n \n {composite_text}"
            else:
                # Fallback to original hardcoded message
                message = (
                    f"The following statements are the flaws others found for agent {source_agent_name}'s response."
                    f" Organize their responses by topic in an additive manner (that is, do not eliminate information)."
                    f" Structure your response using the following sections: 'Agreement', 'Disagreement', and 'Unique observations'."
                    f" In 'Agreement', list ideas supported by multiple agents. In 'Disagreement', note contradictory statements."
                    f" In 'Unique observations', highlight observations made by only one agent."
                    f" The agent under review needs detailed responses to be able to improve. Produce the content for these sections with detailed bulletpoints. \n \n {composite_text}"
                )
            
            # Store the message that was sent
            messages[agent.name] = message
            
            try:
                response = self.send_message_with_integrity(agent, message)
                responses[agent.name] = response
            except Exception as e:
                responses[agent.name] = f"Error: {e}"
        
        return responses, messages


    def send_reflection_analysis(self, target_agent_name):
        """
        Send reflection analysis to target agent with blockchain integrity.
        """
        target_agent = None
        for agent in self.agents:
            if agent.name == target_agent_name:
                target_agent = agent
                break
        
        if not target_agent:
            print(f"Target agent {target_agent_name} not found")
            return None
        
        # Collect reflections from harmonizer agents
        reflections = []
        for agent in self.get_harmonizer_agents():
            if agent.latest_response and agent.latest_response.strip():
                reflections.append(agent.latest_response.strip())
        
        if not reflections:
            print("No reflections found from harmonizer agents")
            return None
        
        composite = "---".join(reflections)
        message = (
            "Judgment of your response has resulted in the observations that follow. "
            "Regenerate your version of the text under review taking into account the consensus of these observations. If you object to an observation, explain why. \n \n " + composite
        )
        
        try:
            response = self.send_message_with_integrity(target_agent, message)
            return response
        except Exception as e:
            return f"Error: {e}"
    
    def get_integrity_report_for_agent(self, agent_name):
        """Get comprehensive integrity report for a specific agent"""
        agent = self.get_agent_by_name(agent_name)
        if not agent:
            return {"error": f"Agent {agent_name} not found"}
        
        history = agent.history_data.get('history', [])
        return self.integrity_manager.get_integrity_report(agent_name, history)
    
    def get_all_integrity_reports(self):
        """Get integrity reports for all agents"""
        reports = {}
        for agent in self.agents:
            reports[agent.name] = self.get_integrity_report_for_agent(agent.name)
        return reports
    
    def rebuild_agent_chain_from_index(self, agent_name, start_index):
        """
        Rebuild blockchain for an agent from a specific index.
        Use this when user legitimately edits conversation history.
        """
        agent = self.get_agent_by_name(agent_name)
        if not agent:
            return False, f"Agent {agent_name} not found"
        
        try:
            history = agent.history_data.get('history', [])
            rebuilt_history = self.integrity_manager.rebuild_agent_chain(agent_name, history, start_index)
            
            # Update agent's history
            agent.history_data['history'] = rebuilt_history
            if hasattr(agent, 'display_history'):
                agent.display_history = rebuilt_history
            
            # Save the rebuilt conversation
            agent.save_conversation()
            
            # Update integrity status
            agent.integrity_issues = []
            agent.integrity_valid = True
            
            print(f"Successfully rebuilt blockchain for {agent_name} from index {start_index}")
            return True, f"Blockchain rebuilt for {agent_name}"
            
        except Exception as e:
            error_msg = f"Error rebuilding blockchain for {agent_name}: {e}"
            print(error_msg)
            return False, error_msg
    
    def reset_all_agents(self):
        """Reset all agents and ask them to introduce themselves with blockchain integrity"""
        print("Resetting all agents...")
        responses = {}
        
        for agent in self.agents:
            try:
                agent.reset_conversation()
                # Clear integrity flags
                agent.integrity_issues = []
                agent.integrity_valid = True
                
                response = self.send_message_with_integrity(agent, "Introduce yourself.")
                responses[agent.name] = response
            except Exception as e:
                responses[agent.name] = f"Error resetting: {e}"
        
        print("All agents reset and asked to introduce themselves")
        return responses
    
    def load_agent_files(self, folder_path):
        """
        Load JSON files for each agent from a folder with integrity verification.
        """
        if not os.path.exists(folder_path):
            print(f"Folder not found: {folder_path}")
            return {}
        
        print(f"Loading agent JSON files from: {folder_path}")
        
        results = {}
        for agent in self.agents:
            agent_name = agent.name
            
            # Try different JSON file naming patterns
            possible_files = [
                f"{agent_name}.json",
                f"{agent_name.lower()}.json",
                f"{agent_name.replace(' ', '_')}.json",
                f"{agent_name.replace(' ', '-')}.json"
            ]
            
            file_loaded = False
            for filename in possible_files:
                file_path = os.path.join(folder_path, filename)
                
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            json_data = json.load(f)
                        
                        # Check if this is a chat history file
                        if isinstance(json_data, dict) and 'history' in json_data:
                            print(f"Loading chat history from {filename} for agent {agent_name}")
                            
                            # Fix missing timestamps and IDs before restoring
                            json_data = self._fix_missing_metadata(json_data, agent)
                            
                            # Migrate to blockchain if needed
                            history = json_data.get('history', [])
                            has_blockchain = any('blockchain' in entry for entry in history if isinstance(entry, dict))
                            
                            if not has_blockchain:
                                print(f"Migrating loaded history for {agent_name} to blockchain format...")
                                migrated_history = self.integrity_manager.migrate_existing_history(agent_name, history)
                                json_data['history'] = migrated_history
                            else:
                                # Restore blockchain with saved metadata to maintain salt consistency
                                blockchain_metadata = json_data.get('blockchain_metadata', {})
                                if 'salt' in blockchain_metadata:
                                    self.integrity_manager.get_or_create_blockchain(agent_name, blockchain_metadata)
                                    print(f"Restored blockchain salt for {agent_name}")
                            
                            agent.restore_conversation_from_history(json_data)
                            
                            # Verify integrity of loaded conversation
                            is_valid, errors = self.integrity_manager.verify_agent_integrity(agent_name, json_data['history'])
                            if is_valid:
                                results[agent_name] = f"Chat history loaded from {filename} - Integrity verified ✅"
                                agent.integrity_issues = []
                                agent.integrity_valid = True
                            else:
                                results[agent_name] = f"Chat history loaded from {filename} - ⚠️ INTEGRITY ISSUES DETECTED"
                                agent.integrity_issues = errors
                                agent.integrity_valid = False
                            
                            file_loaded = True
                            break
                        else:
                            # Try to extract content for non-history JSON
                            content = self._extract_content_from_json(json_data)
                            if content and str(content).strip():
                                print(f"Loading JSON content from {filename} for agent {agent_name}")
                                response = self.send_message_with_integrity(agent, str(content).strip())
                                results[agent_name] = f"Content loaded and processed from {filename}"
                                file_loaded = True
                                break
                                
                    except json.JSONDecodeError as e:
                        results[agent_name] = f"Invalid JSON in {filename}: {e}"
                        print(f"Invalid JSON in file {file_path}: {e}")
                    except Exception as e:
                        results[agent_name] = f"Error loading {filename}: {e}"
                        print(f"Error reading file {file_path}: {e}")
            
            if not file_loaded:
                results[agent_name] = f"No JSON file found. Searched: {', '.join(possible_files)}"
                print(f"No JSON file found for agent {agent_name}")
        
        print("Finished loading agent JSON files")
        return results
    
    def _fix_missing_metadata(self, json_data, agent):
        """Fix missing timestamps and chat IDs in loaded JSON data"""
        current_time = datetime.now().isoformat()
        
        # Fix missing timestamps in history
        history = json_data.get('history', [])
        updated_history = []
        
        for entry in history:
            if isinstance(entry, dict) and 'role' in entry and 'content' in entry:
                # Add timestamp if missing
                if 'timestamp' not in entry or not entry['timestamp']:
                    entry['timestamp'] = current_time
                    print(f"Added missing timestamp to {entry['role']} message in loaded file for {agent.name}")
                
                updated_history.append(entry)
        
        json_data['history'] = updated_history
        
        # Fix missing chat ID
        if 'chat_id' not in json_data or not json_data['chat_id']:
            if hasattr(agent, 'thread'):
                # OpenAI agent - use thread ID
                json_data['chat_id'] = agent.thread.id
                print(f"Added missing thread ID to loaded file for {agent.name}: {agent.thread.id}")
            else:
                # Claude agent - generate UUID
                import uuid
                json_data['chat_id'] = str(uuid.uuid4())
                print(f"Generated missing chat ID for loaded file for {agent.name}: {json_data['chat_id']}")
        
        return json_data
    
    def _extract_content_from_json(self, json_data):
        """Extract content from JSON - helper method"""
        content = None
        possible_keys = ['content', 'message', 'text', 'prompt', 'query', 'input']
        
        for key in possible_keys:
            if key in json_data:
                content = json_data[key]
                break
        
        # If no specific key found, try to use the entire JSON as string
        if content is None:
            if isinstance(json_data, str):
                content = json_data
            elif isinstance(json_data, dict):
                # Convert dict to readable format
                content = json.dumps(json_data, indent=2)
            else:
                content = str(json_data)
        
        return content
    
    def get_agent_by_name(self, name):
        """Get agent by name"""
        for agent in self.agents:
            if agent.name == name:
                return agent
        return None
    
    def get_system_status(self):
        """Get status of all agents including integrity information"""
        status = {
            "total_agents": len(self.agents),
            "active_agents": len(self.get_active_agents()),
            "harmonizer_agents": len(self.get_harmonizer_agents()),
            "non_harmonizer_agents": len(self.get_non_harmonizer_agents()),
            "agents": []
        }
        
        for agent in self.agents:
            agent_info = agent.get_info()
            agent_info["harmonizer"] = getattr(agent, 'harmonizer', False)
            agent_info["integrity_valid"] = getattr(agent, 'integrity_valid', True)
            agent_info["integrity_issues"] = getattr(agent, 'integrity_issues', [])
            status["agents"].append(agent_info)
        
        return status
    
    def run_command_line_interface(self):
        """
        Run a command-line interface for the multi-agent system with blockchain integrity.
        """
        print("*****************   M U L T I - A G E N T   C H A T   *****************")
        print("                    WITH BLOCKCHAIN INTEGRITY                         ")
        
        status = self.get_system_status()
        print(f"Initialized {status['total_agents']} agents ({status['active_agents']} active)")
        
        # Show integrity status
        integrity_issues = sum(1 for agent_info in status["agents"] if not agent_info.get("integrity_valid", True))
        if integrity_issues > 0:
            print(f"⚠️  {integrity_issues} agents have integrity issues!")
        else:
            print("✅ All agents have verified conversation integrity")
        
        for agent_info in status["agents"]:
            integrity_status = "✅" if agent_info.get("integrity_valid", True) else "⚠️"
            print(f"  {integrity_status} {agent_info['name']}: {agent_info['model']} ({'Harmonizer' if agent_info.get('harmonizer') else 'Standard'})")
        
        print("\nCommands:")
        print("  'exit' - Exit the program")
        print("  'reset' - Reset all agents")
        print("  'status' - Show system status")
        print("  'integrity' - Show integrity reports for all agents")
        print("  'integrity <agent_name>' - Show integrity report for specific agent")
        print("  'rebuild <agent_name> <index>' - Rebuild blockchain from index for agent")
        print("  'load <folder>' - Load conversations from folder")
        print("  'file:<path>' - Upload file (OpenAI agents only)")
        print("  'vuln <agent_name>' - Run vulnerability analysis")
        print("  'judge <agent_name>' - Run judgment analysis")
        print("  'reflect <agent_name>' - Run reflection analysis")
        print("  Any other text will be broadcast to all active agents")
        
        while True:
            print("\n>>>>>>>>>>>>>>>>>>>>>>>>>>")
            user_input = input(f"{self.user}: ")
            
            if user_input.lower() == 'exit':
                break
            elif user_input.lower() == 'reset':
                responses = self.reset_all_agents()
                for name, response in responses.items():
                    print(f"\n{name}: {response}")
            elif user_input.lower() == 'status':
                status = self.get_system_status()
                print(f"\nSystem Status:")
                print(f"  Total agents: {status['total_agents']}")
                print(f"  Active agents: {status['active_agents']}")
                print(f"  Harmonizer agents: {status['harmonizer_agents']}")
                for agent_info in status["agents"]:
                    active_status = "Active" if agent_info["active"] else "Inactive"
                    harmonizer_status = " (Harmonizer)" if agent_info.get("harmonizer") else ""
                    integrity_status = "✅" if agent_info.get("integrity_valid", True) else "⚠️"
                    print(f"    {integrity_status} {agent_info['name']}: {active_status}{harmonizer_status}")
            elif user_input.lower() == 'integrity':
                reports = self.get_all_integrity_reports()
                for agent_name, report in reports.items():
                    print(f"\n--- {agent_name} Integrity Report ---")
                    if report.get('integrity_valid', False):
                        print("✅ Conversation integrity verified")
                    else:
                        print("⚠️ INTEGRITY ISSUES DETECTED:")
                        for error in report.get('errors', []):
                            print(f"   - {error}")
            elif user_input.startswith('integrity '):
                agent_name = user_input[10:].strip()
                report = self.get_integrity_report_for_agent(agent_name)
                print(f"\n--- {agent_name} Integrity Report ---")
                if 'error' in report:
                    print(f"Error: {report['error']}")
                elif report.get('integrity_valid', False):
                    print("✅ Conversation integrity verified")
                    print(f"Total blocks: {report.get('metadata', {}).get('total_blocks', 0)}")
                else:
                    print("⚠️ INTEGRITY ISSUES DETECTED:")
                    for error in report.get('errors', []):
                        print(f"   - {error}")
            elif user_input.startswith('rebuild '):
                parts = user_input[8:].strip().split()
                if len(parts) >= 2:
                    agent_name = parts[0]
                    try:
                        start_index = int(parts[1])
                        success, message = self.rebuild_agent_chain_from_index(agent_name, start_index)
                        print(f"Rebuild result: {message}")
                    except ValueError:
                        print("Error: Index must be a number")
                else:
                    print("Usage: rebuild <agent_name> <start_index>")
            elif user_input.startswith('load '):
                folder_path = user_input[5:].strip()
                results = self.load_agent_files(folder_path)
                for name, result in results.items():
                    print(f"{name}: {result}")
            elif user_input.startswith('file:'):
                file_path = user_input[5:].strip()
                # Upload to OpenAI agents only
                for agent in self.get_active_agents():
                    if hasattr(agent, 'upload_file'):
                        try:
                            file_id = agent.upload_file(file_path)
                            if file_id:
                                print(f"File uploaded to {agent.name}: {file_id}")
                        except Exception as e:
                            print(f"Error uploading to {agent.name}: {e}")
                    else:
                        print(f"File upload not supported for {agent.name} (Claude agent)")
            elif user_input.startswith('vuln '):
                agent_name = user_input[5:].strip()
                responses = self.send_vulnerability_analysis(agent_name)
                for name, response in responses.items():
                    print(f"\n{name}: {response}")
            elif user_input.startswith('judge '):
                agent_name = user_input[6:].strip()
                responses = self.send_judgment_analysis(agent_name)
                for name, response in responses.items():
                    print(f"\n{name}: {response}")
            elif user_input.startswith('reflect '):
                agent_name = user_input[8:].strip()
                response = self.send_reflection_analysis(agent_name)
                if response:
                    print(f"\n{agent_name}: {response}")
            else:
                # Broadcast message to all active agents with blockchain integrity
                responses = self.broadcast_message(user_input)
                print("\n<<<<<<<<<<<<<<<<<<<<<<<<<<")
                for name, response in responses.items():
                    print(f"\n{name}: {response}")


# Example usage and testing
if __name__ == "__main__":
    try:
        orchestrator = MultiAgentOrchestrator()
        orchestrator.run_command_line_interface()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")