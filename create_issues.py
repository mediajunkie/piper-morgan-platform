#!/usr/bin/env python3
"""
Piper Morgan 1.0 - GitHub Issues Generator - Fixed Parser
Creates GitHub issues from backlog document for project management
Date: June 6, 2025
"""

import os
import sys
import json
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from github import Github
from github.GithubException import GithubException
import argparse
from datetime import datetime

# ANSI color codes for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

def print_status(message: str):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")

def print_success(message: str):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

def print_error(message: str):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

@dataclass
class BacklogItem:
    """Represents a backlog item parsed from markdown"""
    id: str
    title: str
    description: str
    story: str
    acceptance_criteria: List[str]
    estimate: int
    priority: str
    status: str
    dependencies: List[str]
    labels: List[str]
    assignee: Optional[str] = None
    milestone: Optional[str] = None

class BacklogParser:
    """Parse backlog markdown and extract GitHub issues"""
    
    def __init__(self, backlog_content: str):
        self.content = backlog_content
        self.items: List[BacklogItem] = []
    
    def parse(self) -> List[BacklogItem]:
        """Parse the markdown content and extract backlog items"""
        print_status("Parsing backlog document...")
        
        # Split content into sections
        sections = self._split_into_sections()
        print_status(f"Found {len(sections)} priority sections")
        
        for section in sections:
            items = self._parse_section(section)
            self.items.extend(items)
        
        print_success(f"Parsed {len(self.items)} backlog items")
        return self.items
    
    def _split_into_sections(self) -> List[str]:
        """Split markdown into priority sections"""
        sections = []
        current_section = []
        
        lines = self.content.split('\n')
        in_section = False
        
        for line in lines:
            # Fixed: More flexible pattern matching for section headers
            if re.match(r'^## 🔥.*P0', line):
                if current_section and in_section:
                    sections.append('\n'.join(current_section))
                current_section = [line]
                in_section = True
                print_status(f"Found section: {line[:50]}...")
            elif re.match(r'^## 🎯.*P1', line):
                if current_section and in_section:
                    sections.append('\n'.join(current_section))
                current_section = [line]
                in_section = True
                print_status(f"Found section: {line[:50]}...")
            elif re.match(r'^## 📈.*P2', line):
                if current_section and in_section:
                    sections.append('\n'.join(current_section))
                current_section = [line]
                in_section = True
                print_status(f"Found section: {line[:50]}...")
            elif re.match(r'^## 🚀.*P3', line):
                if current_section and in_section:
                    sections.append('\n'.join(current_section))
                current_section = [line]
                in_section = True
                print_status(f"Found section: {line[:50]}...")
            elif re.match(r'^## 🔬.*Research', line):
                if current_section and in_section:
                    sections.append('\n'.join(current_section))
                current_section = [line]
                in_section = True
                print_status(f"Found section: {line[:50]}...")
            elif line.startswith('## ') and in_section:
                # Hit a different section, save current and stop processing this section
                if current_section:
                    sections.append('\n'.join(current_section))
                    print_status(f"Ending section, found: {line[:50]}...")
                current_section = []
                in_section = False
            elif in_section:
                current_section.append(line)
        
        # Don't forget the last section
        if current_section and in_section:
            sections.append('\n'.join(current_section))
        
        # Debug: show section info
        for i, section in enumerate(sections):
            section_lines = section.split('\n')
            header = section_lines[0] if section_lines else "Unknown"
            print_status(f"Section {i+1}: {header[:50]}... ({len(section)} chars)")
        
        return sections
    
    def _parse_section(self, section: str) -> List[BacklogItem]:
        """Parse individual section for backlog items"""
        items = []
        
        # Extract priority from section header
        priority = self._extract_priority(section)
        print_status(f"Parsing {priority} section...")
        
        # Find all items in section (start with ###)
        # Updated pattern to handle the specific format with separate lines
        item_pattern = r'### (PM-[^:]+): (.+?)\n(.*?)(?=### |---|\Z)'
        matches = re.findall(item_pattern, section, re.DOTALL)
        
        print_status(f"Found {len(matches)} items in {priority} section")
        
        for match in matches:
            item_id, title, content = match
            print_status(f"Parsing item: {item_id}")
            item = self._parse_item(item_id, title, content, priority)
            if item:
                items.append(item)
        
        return items
    
    def _extract_priority(self, section: str) -> str:
        """Extract priority level from section header"""
        if '🔥' in section and 'P0' in section:
            return 'P0'
        elif '🎯' in section and 'P1' in section:
            return 'P1'
        elif '📈' in section and 'P2' in section:
            return 'P2'
        elif '🚀' in section and 'P3' in section:
            return 'P3'
        elif '🔬' in section and 'Research' in section:
            return 'Research'
        return 'Unknown'
    
    def _parse_item(self, item_id: str, title: str, content: str, priority: str) -> Optional[BacklogItem]:
        """Parse individual backlog item"""
        try:
            # Extract story from **Story**: line
            story_match = re.search(r'\*\*Story\*\*:\s*(.+?)(?:\n|$)', content)
            story = story_match.group(1).strip() if story_match else f"As a user, I want {title}"
            
            # Extract description - try multiple patterns
            description = ""
            for pattern in [
                r'\*\*Current State\*\*:\s*(.+?)(?:\n\*\*|\n\Z)',
                r'\*\*Description\*\*:\s*(.+?)(?:\n\*\*|\n\Z)',
                r'\*\*Reality Check\*\*:\s*(.+?)(?:\n\*\*|\n\Z)'
            ]:
                desc_match = re.search(pattern, content, re.DOTALL)
                if desc_match:
                    description = desc_match.group(1).strip()
                    break
            
            if not description:
                description = content[:200] + "..."
            
            # Extract acceptance criteria from **Acceptance Criteria**: section
            criteria = []
            criteria_match = re.search(r'\*\*Acceptance Criteria\*\*:\s*\n((?:- .+\n?)*)', content)
            if criteria_match:
                criteria_text = criteria_match.group(1)
                criteria = [line.strip('- ').strip() for line in criteria_text.split('\n')
                           if line.strip() and line.strip().startswith('-')]
            
            # Extract estimate from **Estimate**: X points pattern
            estimate_match = re.search(r'\*\*Estimate\*\*:\s*(\d+)\s*points?', content)
            estimate = int(estimate_match.group(1)) if estimate_match else 5
            
            # Extract status/current state
            status = "Not Started"
            status_patterns = [
                r'\*\*Current State\*\*:\s*(.+?)(?:\n|\|)',
                r'\*\*Status\*\*:\s*(.+?)(?:\n|\|)'
            ]
            for pattern in status_patterns:
                status_match = re.search(pattern, content)
                if status_match:
                    status = status_match.group(1).strip()
                    # Clean up status (remove emojis and extra formatting)
                    status = re.sub(r'🚨|⚠️|📋|✅', '', status).strip()
                    status = re.sub(r'\*\*', '', status).strip()
                    break
            
            # Extract dependencies from **Dependencies**: line
            dependencies = []
            deps_match = re.search(r'\*\*Dependencies\*\*:\s*(.+?)(?:\n|$)', content)
            if deps_match:
                deps_text = deps_match.group(1)
                if 'None' not in deps_text:
                    dependencies = [dep.strip() for dep in deps_text.split(',') if dep.strip()]
            
            # Generate labels based on priority and content
            labels = self._generate_labels(priority, title, content, status, estimate)
            
            print_success(f"Successfully parsed {item_id}: {title[:50]}...")
            
            return BacklogItem(
                id=item_id,
                title=title,
                description=description,
                story=story,
                acceptance_criteria=criteria,
                estimate=estimate,
                priority=priority,
                status=status,
                dependencies=dependencies,
                labels=labels
            )
            
        except Exception as e:
            print_warning(f"Failed to parse item {item_id}: {e}")
            print_warning(f"Content preview: {content[:100]}...")
            return None
    
    def _generate_labels(self, priority: str, title: str, content: str, status: str, estimate: int) -> List[str]:
        """Generate appropriate GitHub labels for the issue"""
        labels = []
        
        # Priority labels
        priority_map = {
            'P0': 'priority: critical',
            'P1': 'priority: high',
            'P2': 'priority: medium',
            'P3': 'priority: low',
            'Research': 'type: research'
        }
        if priority in priority_map:
            labels.append(priority_map[priority])
        
        # Type labels based on content
        title_lower = title.lower()
        content_lower = content.lower()
        
        if any(word in title_lower for word in ['database', 'schema', 'migration']):
            labels.append('component: database')
        if any(word in title_lower for word in ['ui', 'interface', 'web']):
            labels.append('component: ui')
        if any(word in title_lower for word in ['api', 'endpoint']):
            labels.append('component: api')
        if any(word in title_lower for word in ['github', 'integration']):
            labels.append('component: integration')
        if any(word in title_lower for word in ['workflow', 'orchestration']):
            labels.append('component: workflow')
        if any(word in title_lower for word in ['knowledge', 'search']):
            labels.append('component: knowledge')
        if any(word in title_lower for word in ['intent', 'classification']):
            labels.append('component: ai')
        
        # Status labels
        if 'critical' in status.lower() or 'blocking' in status.lower():
            labels.append('status: blocked')
        elif 'missing' in status.lower() or 'not implemented' in status.lower():
            labels.append('status: needs-implementation')
        elif 'partial' in status.lower() or 'quality issue' in status.lower():
            labels.append('status: needs-improvement')
        
        # Size labels based on estimate
        if estimate <= 3:
            labels.append('size: small')
        elif estimate <= 8:
            labels.append('size: medium')
        else:
            labels.append('size: large')
        
        return labels

class GitHubIssueCreator:
    """Create GitHub issues from backlog items"""
    
    def __init__(self, token: str, repo_name: str):
        self.github = Github(token)
        self.repo = self.github.get_repo(repo_name)
        self.created_issues = []
    
    def create_issues(self, items: List[BacklogItem], dry_run: bool = True) -> List[Dict]:
        """Create GitHub issues from backlog items"""
        print_status(f"Creating {len(items)} GitHub issues...")
        if dry_run:
            print_warning("DRY RUN MODE - No issues will be created")
        
        results = []
        
        for item in items:
            try:
                if dry_run:
                    result = self._simulate_issue_creation(item)
                else:
                    result = self._create_issue(item)
                results.append(result)
                
            except Exception as e:
                print_error(f"Failed to create issue {item.id}: {e}")
                results.append({
                    'id': item.id,
                    'success': False,
                    'error': str(e)
                })
        
        success_count = len([r for r in results if r.get('success', False)])
        print_success(f"Successfully processed {success_count}/{len(items)} issues")
        
        return results
    
    def _simulate_issue_creation(self, item: BacklogItem) -> Dict:
        """Simulate issue creation for dry run"""
        print_status(f"[DRY RUN] Would create: {item.id} - {item.title}")
        print_status(f"  Priority: {item.priority} | Estimate: {item.estimate} points")
        print_status(f"  Labels: {', '.join(item.labels)}")
        if item.acceptance_criteria:
            print_status(f"  Acceptance Criteria: {len(item.acceptance_criteria)} items")
        return {
            'id': item.id,
            'title': item.title,
            'labels': item.labels,
            'estimate': item.estimate,
            'success': True,
            'url': f"https://github.com/example/repo/issues/123",
            'dry_run': True
        }
    
    def _create_issue(self, item: BacklogItem) -> Dict:
        """Create actual GitHub issue"""
        try:
            # Format issue body
            body = self._format_issue_body(item)
            
            print_status(f"Creating issue: [{item.id}] {item.title}")
            print_status(f"  Labels: {item.labels}")
            print_status(f"  Body length: {len(body)} characters")
            
            # Create issue with you as assignee
            issue = self.repo.create_issue(
                title=f"[{item.id}] {item.title}",
                body=body,
                labels=item.labels,
                assignee="mediajunkie"  # Assign to you
            )
            
            print_success(f"Created issue #{issue.number}: {item.title}")
            
            return {
                'id': item.id,
                'title': item.title,
                'number': issue.number,
                'url': issue.html_url,
                'labels': item.labels,
                'estimate': item.estimate,
                'success': True
            }
            
        except Exception as e:
            print_error(f"Detailed error for {item.id}: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'id': item.id,
                'title': item.title,
                'success': False,
                'error': f"{type(e).__name__}: {str(e)}"
            }
    
    def _format_issue_body(self, item: BacklogItem) -> str:
        """Format GitHub issue body from backlog item"""
        body_parts = []
        
        # Story
        body_parts.append(f"**User Story**\n{item.story}\n")
        
        # Description
        body_parts.append(f"**Description**\n{item.description}\n")
        
        # Acceptance Criteria
        if item.acceptance_criteria:
            body_parts.append("**Acceptance Criteria**")
            for criteria in item.acceptance_criteria:
                body_parts.append(f"- [ ] {criteria}")
            body_parts.append("")
        
        # Technical Details
        tech_details = []
        tech_details.append(f"**Priority**: {item.priority}")
        tech_details.append(f"**Estimate**: {item.estimate} story points")
        tech_details.append(f"**Status**: {item.status}")
        
        if item.dependencies:
            tech_details.append(f"**Dependencies**: {', '.join(item.dependencies)}")
        
        body_parts.append("**Technical Details**")
        body_parts.extend(tech_details)
        body_parts.append("")
        
        # Footer
        body_parts.append("---")
        body_parts.append(f"*Generated from backlog on {datetime.now().strftime('%Y-%m-%d')}*")
        body_parts.append(f"*Issue ID: {item.id}*")
        
        return "\n".join(body_parts)

def load_backlog_content(file_path: str) -> str:
    """Load backlog markdown content from file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print_error(f"Backlog file not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Failed to read backlog file: {e}")
        sys.exit(1)

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Generate GitHub issues from Piper Morgan backlog')
    parser.add_argument('--backlog', '-b',
                       default='backlog.md',
                       help='Path to backlog markdown file')
    parser.add_argument('--repo', '-r',
                       required=True,
                       help='GitHub repository (owner/repo)')
    parser.add_argument('--token', '-t',
                       help='GitHub token (or set GITHUB_TOKEN env var)')
    parser.add_argument('--dry-run',
                       action='store_true',
                       help='Simulate issue creation without actually creating them')
    parser.add_argument('--filter-priority', '-p',
                       choices=['P0', 'P1', 'P2', 'P3', 'Research'],
                       help='Only create issues for specific priority')
    parser.add_argument('--output', '-o',
                       help='Save results to JSON file')
    
    args = parser.parse_args()
    
    # Get GitHub token
    token = args.token or os.getenv('GITHUB_TOKEN')
    if not token:
        print_error("GitHub token required. Use --token or set GITHUB_TOKEN environment variable")
        sys.exit(1)
    
    print_status("Piper Morgan GitHub Issues Generator")
    print_status(f"Repository: {args.repo}")
    print_status(f"Backlog file: {args.backlog}")
    print_status(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    
    # Load and parse backlog
    backlog_content = load_backlog_content(args.backlog)
    parser = BacklogParser(backlog_content)
    items = parser.parse()
    
    # Filter by priority if specified
    if args.filter_priority:
        items = [item for item in items if item.priority == args.filter_priority]
        print_status(f"Filtered to {len(items)} items with priority {args.filter_priority}")
    
    if not items:
        print_warning("No backlog items found to process")
        return
    
    # Create GitHub issues
    try:
        creator = GitHubIssueCreator(token, args.repo)
        results = creator.create_issues(items, dry_run=args.dry_run)
        
        # Save results if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print_success(f"Results saved to {args.output}")
        
        # Summary
        print_status("\nSummary:")
        print(f"  Total items processed: {len(results)}")
        print(f"  Successful: {len([r for r in results if r.get('success')])}")
        print(f"  Failed: {len([r for r in results if not r.get('success')])}")
        
        if args.dry_run:
            print_warning("\nThis was a dry run. Remove --dry-run to actually create issues.")
    
    except GithubException as e:
        print_error(f"GitHub API error: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
