## System Data Flow Diagram

```mermaid
graph TD
    Start([Banner Request]) -->|Items, Caption, Event Code| Validate["Validate Event<br/>and Inputs"]
    Validate -->|Valid| Config["Load Event Config<br/>events.json"]
    Validate -->|Invalid| Error["Return Error<br/>to User"]
    Config -->|Background Path| Background["Select Background<br/>bg/*.png or bg.png"]
    Config -->|Theme Colors| Transform["Compose Banner<br/>Products, Spacer, Caption"]
    Background --> Transform
    Transform -->|Processed| Output["Generate WEBP<br/>Banner File"]
    Output -->|Result| End([User Receives Result])
    Error -->|Feedback| Start
    
    style Start fill:#e1f5fe
    style Validate fill:#ffe0b2
    style Config fill:#ffe0b2
    style Background fill:#f3e5f5
    style Transform fill:#f3e5f5
    style Output fill:#e8f5e8
    style Error fill:#ffebee
    style End fill:#e8f5e8
```

## Legend

- **Blue (Cyan)**: User interaction points
- **Orange**: Processing/validation steps  
- **Purple**: Data transformation
- **Green**: Storage and output operations
- **Red**: Error handling

## Description

This diagram shows the banner generation data flow. Users provide item numbers, caption text, and an event code. Valid requests load event configuration, select the configured event background, compose product imagery with themed caption elements, and generate a WEBP output. Invalid requests return actionable errors.

**Key Components:**
- Event and input validation with error feedback loop
- Event configuration-driven background and theme selection
- Product image and caption composition
- WEBP output generation and delivery

Update this diagram when adding new data processing stages or changing the core system flow.
