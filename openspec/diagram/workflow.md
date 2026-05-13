## User Workflow Diagram

```mermaid
graph TD
    Start([User Starts]) -->|Access| Landing["Application<br/>Landing/Home"]
    Landing -->|Navigate| Action1["Primary Action<br/>Main Feature"]
    Landing -->|Navigate| Action2["Secondary Action<br/>Alternative Path"]
    
    Action1 -->|Input| Form1["Fill Form<br/>Required Fields"]
    Action2 -->|Configure| Setup["Configuration<br/>Settings/Preferences"]
    
    Form1 -->|Submit| Validate1{Validation<br/>Check}
    Setup -->|Save| Validate2{Validation<br/>Check}
    
    Validate1 -->|Pass| Process1["Process Request<br/>Execute Action"]
    Validate1 -->|Fail| Error1["Show Errors<br/>Return to Form"]
    Error1 --> Form1
    
    Validate2 -->|Pass| Process2["Save Settings<br/>Apply Configuration"]  
    Validate2 -->|Fail| Error2["Show Errors<br/>Return to Setup"]
    Error2 --> Setup
    
    Process1 -->|Complete| Success1["Success State<br/>Show Results"]
    Process2 -->|Complete| Success2["Settings Saved<br/>Confirmation"]
    
    Success1 -->|Continue| End([Workflow Complete])
    Success2 -->|Continue| End
    
    style Start fill:#e1f5fe
    style Landing fill:#e1f5fe
    style Action1 fill:#e1f5fe
    style Action2 fill:#e1f5fe
    style Form1 fill:#e1f5fe
    style Setup fill:#e1f5fe
    style Validate1 fill:#ffe0b2
    style Validate2 fill:#ffe0b2
    style Process1 fill:#f3e5f5
    style Process2 fill:#f3e5f5
    style Success1 fill:#e8f5e8
    style Success2 fill:#e8f5e8
    style Error1 fill:#ffebee
    style Error2 fill:#ffebee
    style End fill:#e8f5e8
```

## Workflow Description

This diagram represents the typical user journey through the application. Users start at a landing point and can choose between primary and secondary actions. Each path includes form filling or configuration, validation with error handling, processing, and success states.

**Key Features:**
- Multiple user entry paths
- Form validation with error feedback loops
- Clear success/error states
- Consistent user experience patterns

**Interaction Patterns:**
- All forms include validation with error recovery
- Success states provide clear feedback  
- Error states guide users back to correction points
- Workflow supports both primary and alternative user goals

Update this diagram when adding new user interaction paths or changing the core user experience flow.
