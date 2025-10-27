# Milestone Manager

## Overview
Milestone Manager is a desktop application designed to visualize timeline-based milestones and events. Built with PyQt6, it offers a modern, Apple-style intuitive user interface. All project data is stored locally in JSON files, ensuring data ownership and transparency. The application aims to provide a clear, concise, and interactive way to manage and track project timelines, making it suitable for reporting and presentations.

## User Preferences
- **Design**: Light mode preferred (dark mode not preferred).
- All code should use Korean comments and docstrings.
- Adhere to PEP 8 style guide.
- Use clear variable and function names.
- Code structure should be modularized.
- Apple-style modern UI/UX is preferred.

## System Architecture
The application is structured into several Python modules:
- `main.py`: Entry point for the application, handling login and license management.
- `data_manager.py`: Manages data persistence to and from `raw.json`.
- `ui_main_window.py`: Defines the main application window and its components.
- `timeline_canvas.py`: Handles the visual rendering and interaction of the timeline.
- `custom_widgets.py`: Contains custom PyQt widgets for specific UI elements.

### UI/UX Decisions
- **Design Theme**: Predominantly light theme, inspired by Apple's aesthetic, featuring white backgrounds and clean outlines.
- **Color Palette**:
    - Primary Blue: `#007AFF`
    - Background: `#f5f5f7`, `#ffffff`
    - Text: `#1d1d1f`
    - Secondary: `#86868b`
    - Border: `#d2d2d7`, `#e8e8ed`
- **Typography**: Apple SD Gothic Neo font for a sleek, modern look.
- **Interactivity**: Smooth interactions with hover effects and clear feedback for selected states and buttons.
- **Responsiveness**: UI elements scaled for optimal viewing on 1920x1080 resolution, with adjustable padding and margins.

### Technical Implementations
- **Timeline Visualization**: Features quarterly (e.g., 24.Q1) and monthly scales, dynamic year expansion to include current and intermediate years, and "This Month" indicator.
- **Node Management**: Nodes (events) can be customized by shape, color, date (YY.MM or YY.Qn format with validation), content, memo (tooltip on hover), and attached files. Selection is via checkboxes, allowing one node at a time for modification or deletion.
- **Data Persistence**: All data is stored in `raw.json`. Automatic loading on startup, real-time status display, warning for empty saves, and automatic backups (`raw.json.backup`) are implemented for data safety.
- **Search and Filter**: Capabilities include keyword search across milestone titles/subtitles, content search within nodes, shape-based filtering, and date-based filtering by year and quarter. A "This Month" filter is also available.
- **Image Export**: Individual milestone blocks can be exported as PNG/JPG images, automatically saved to a `Milestone_IMG` folder.
- **Zoom and Pan** (Updated 2025-10-27): The timeline view supports smooth zooming and panning using mouse wheel (Ctrl+wheel for fine adjustment) and drag functionalities. A new "🔍 확대 보기" button on each milestone block opens a ZoomableTimelineDialog (1200x700) with ➕/➖ zoom buttons, ⊡ fit-to-view button, and interactive zoom/pan controls for detailed timeline inspection.
- **Node Layout**: Improved node placement logic prevents overlapping, distributing nodes with the same date for better readability.

### Feature Specifications
- **Login and License**: Hardcoded credentials (`MCI / mci2025!`) and a license expiration date (2025-12-31) with warning notifications.
- **Milestone Block Management**: Supports creation, deletion, and inline editing of milestone titles and subtitles.
- **Keyboard Shortcuts**: Streamlined shortcuts for data loading (Ctrl+L), node addition (Ctrl+N), editing (Ctrl+E), and deletion (Ctrl+D).

## External Dependencies
- **GUI Framework**: PyQt6
- **Image Processing**: Pillow (PIL)
- **Data Storage**: JSON (standard Python library)