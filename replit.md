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
- **Node Management**: Nodes (events) can be customized by shape, color, date (YY.MM or YY.Qn format with validation), content, memo (tooltip on hover), and attached files. Each node now supports a second optional shape and color (shape2, color2) to distinguish multiple items on the same date (e.g., different equipment types). Selection is via checkboxes, allowing one node at a time for modification or deletion.
- **Data Persistence**: All data is stored in `raw.json`. Automatic loading on startup, real-time status display, warning for empty saves, and automatic backups (`raw.json.backup`) are implemented for data safety.
- **Search and Filter**: Capabilities include keyword search across milestone titles/subtitles, content search within nodes, shape-based filtering, and date-based filtering by year and quarter. A "This Month" filter is also available.
- **Image Export**: Individual milestone blocks can be exported as PNG/JPG images, automatically saved to a `Milestone_IMG` folder.
- **Zoom and Pan** (Updated 2025-10-27): The timeline view supports smooth zooming and panning using mouse wheel (Ctrl+wheel for fine adjustment) and drag functionalities. A new "🔍 확대 보기" button on each milestone block opens a ZoomableTimelineDialog (1200x700) with ➕/➖ zoom buttons, ⊡ fit-to-view button, and interactive zoom/pan controls for detailed timeline inspection.
- **Node Layout** (Updated 2025-10-28): Dynamic height reallocation algorithm implemented for optimal timeline proximity. Nodes are grouped quarterly (1,3,5 / 2,4,6 / 7,9,11 / 8,10,12) and positioned based on actual data presence within each group. When fewer months have data in a group, positions are reallocated to keep nodes closer to the timeline. Example: if only month 5 exists in the 1,3,5 group, it positions at +60 (closest) instead of +180 (farthest). When month 3 is added, month 3 gets +60 and month 5 moves to +120. Full group (1,3,5) uses all positions (+60/+120/+180). This improves visual proximity and readability, especially for sparse datasets. Multiple nodes in the same month are distributed horizontally only, eliminating vertical overlap issues.
- **UI Optimization** (Updated 2025-10-27): Font sizes reduced across the application (title: 18px, buttons: 11px, node text: 10px/9px) and spacing/padding minimized for better screen real estate utilization. Milestone blocks fixed at 250px height in main UI with internal scrolling enabled. Timeline height standardized to 400px with timeline at y=200 position.

### Feature Specifications
- **Login and License**: Hardcoded credentials (`MCI / mci2025!`) and a license expiration date (2025-12-31) with warning notifications.
- **Milestone Block Management**: Supports creation, deletion, and inline editing of milestone titles and subtitles.
- **Keyboard Shortcuts**: Streamlined shortcuts for data loading (Ctrl+L), node addition (Ctrl+N), editing (Ctrl+E), and deletion (Ctrl+D).

## External Dependencies
- **GUI Framework**: PyQt6
- **Image Processing**: Pillow (PIL)
- **Data Storage**: JSON (standard Python library)