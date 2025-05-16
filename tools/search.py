from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.auth import auth


class SearchTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Search Confluence content using simple keywords or advanced CQL (Confluence Query Language) syntax.
        """
        confluence = auth(self.runtime.credentials)
        
        # Get base URL from credentials
        base_url = self.runtime.credentials.get("url", "").rstrip("/")
        
        # Get common parameters
        limit = tool_parameters.get("limit", 10)  # Default limit is 10
        
        # Get keywords for simple search
        keywords = tool_parameters.get("keywords", "")
        if not keywords:
            yield self.create_text_message("Error: No search keywords provided.")
            return
            
        # Build CQL query
        cql_parts = [f'siteSearch ~ "{keywords}"']
        
        # Add space filter if provided
        space = tool_parameters.get("space")
        if space:
            if isinstance(space, list):
                spaces = space
            else:
                spaces = [s.strip() for s in str(space).split(",") if s.strip()]
            if spaces:
                space_list = ', '.join(f'"{s}"' for s in spaces)
                cql_parts.append(f'space in ({space_list})')
        
        # Add contributor filter if provided
        contributor = tool_parameters.get("contributor")
        if contributor:
            if isinstance(contributor, list):
                contributors = contributor
            else:
                contributors = [c.strip() for c in str(contributor).split(",") if c.strip()]
            if contributors:
                contributor_list = ', '.join(f'"{c}"' for c in contributors)
                cql_parts.append(f'contributor in ({contributor_list})')
        
        # Add content type filter if provided
        content_type = tool_parameters.get("content_type")
        if content_type:
            if isinstance(content_type, list):
                types = content_type
            else:
                types = [t.strip() for t in str(content_type).split(",") if t.strip()]
            if types:
                type_list = ', '.join(f'"{t}"' for t in types)
                cql_parts.append(f'type in ({type_list})')
        
        # Add last modified date filter if provided
        lastmodified = tool_parameters.get("lastmodified")
        if lastmodified and lastmodified != 'anytime':
            cql_parts.append(f'lastmodified >= {lastmodified}')
        
        # Add label filter if provided
        label = tool_parameters.get("label")
        if label:
            if isinstance(label, list):
                labels = label
            else:
                labels = [l.strip() for l in str(label).split(",") if l.strip()]
            if labels:
                labels_list = ", ".join(f'"{l}"' for l in labels)
                cql_parts.append(f'label in ({labels_list})')
        
        # Combine all parts with AND operator
        cql = " AND ".join(cql_parts)
        
        # Perform CQL search
        try:
            # The search method accepts CQL queries
            results = confluence.cql(cql, limit=limit, expand="content.space,content.version,content.history,content.metadata.labels,content.body.view")
            
            # Format the results
            formatted_results = {
                "total": results.get("totalSize", 0),
                "results": [],
                "query": cql
            }
            
            # Process each result
            for result in results.get("results", []):
                content = result.get("content", {})
                history = content.get("history", {})
                version = content.get("version", {})

                formatted_result = {
                    "id": content.get("id"),
                    "type": content.get("type"),
                    "title": content.get("title"),
                    "url": f"{base_url}{content.get('_links', {}).get('webui', '')}",
                    "creator": history.get("createdBy", {}).get("displayName", ""),
                    "created_date": history.get("createdDate", ""),
                    "last_modifier": version.get("by", {}).get("displayName", ""),
                    "last_modified_date": version.get("when", ""),
                    "version_number": version.get("number", ""),
                    "labels": [label.get("name", "") for label in content.get("metadata", {}).get("labels", {}).get("results", [])],
                    "excerpt": result.get("excerpt", ""),
                    "body": content.get("body", {}).get("view", {}).get("value", "") if content.get("body") else ""
                }
                
                # Add space information if available
                if "space" in content:
                    formatted_result["space"] = {
                        "key": content["space"].get("key"),
                        "name": content["space"].get("name")
                    }
                
                formatted_results["results"].append(formatted_result)
            
            yield self.create_json_message(formatted_results)
        except Exception as e:
            yield self.create_text_message(f'CQL query: {cql}\n' + 'Error performing search: {str(e)}')