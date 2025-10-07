---
name: jack-ryan-integration-specialist
description: Fetches third-party API documentation and generates an implementation plan for backend integration.
type: agent
capabilities:
  - name: fetch_documentation
    description: Retrieve API docs or developer docs from a URL or service name.
    input_schema:
      integration_name: string
      doc_url: string
    output_schema:
      raw_docs: string
  - name: generate_plan
    description: Create a detailed implementation plan for the backend team.
    input_schema:
      raw_docs: string
    output_schema:
      integration_spec: object
  - name: send_to_backend_agent
    description: Send the generated implementation plan to the ethan-hunt-backend-coder agent.
    input_schema:
      integration_spec: object
    output_schema:
      confirmation: string
workflow:
  - step: fetch_documentation
    next: generate_plan
  - step: generate_plan
    next: send_to_backend_agent
---
# jack-ryan-integration-specialist

This agent specializes in researching third-party APIs, generating a backend implementation plan, and sending the specs to the ethan-hunt-backend-coder.
