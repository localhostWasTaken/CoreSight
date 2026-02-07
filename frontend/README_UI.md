# CoreSight Admin UI

A Swiss-style utilitarian admin interface for CoreSight - Business Intelligence via Engineering Metrics.

## Design Philosophy

### Swiss Design Principles
- **Minimalism**: Clean, uncluttered interface with purposeful elements
- **Grid System**: 8px baseline grid for consistent spacing
- **Typography**: Strong hierarchy with clear font weights and sizes
- **Color**: Light, professional palette with high contrast
- **Geometry**: Sharp edges (no border-radius), rectangular forms
- **Clarity**: Every element has a clear purpose

### Design System

#### Colors
```css
Background:    rgb(250, 250, 250)  - Light neutral
Surface:       rgb(255, 255, 255)  - Pure white
Accent:        rgb(24, 24, 27)     - Near black
Text Primary:  rgb(24, 24, 27)     - Near black
Text Secondary: rgb(82, 82, 91)    - Medium gray
Border:        rgb(228, 228, 231)  - Light gray
```

#### Components
- **Cards**: White surface with subtle border, no rounded corners
- **Buttons**: Rectangle with clear borders, purposeful hover states
- **Tables**: Clean grid with strong header separation
- **Badges**: Small, bordered labels for status indication
- **Forms**: Minimal inputs with focus states

## Features

### Authentication
- JWT-based authentication system
- Protected routes
- Automatic token management
- Login page with clean form design

### Pages

#### Dashboard
- Overview metrics with stat cards
- Quick actions for common tasks
- System status information
- Navigation to key features

#### Users Management
- List all users with their details
- Add new users with comprehensive form
- Skills tracking and hourly rates
- Integration with GitHub and Jira accounts

#### Tasks
- Task list with filtering by status
- Status indicators (To Do, In Progress, Done, Blocked)
- Priority badges
- Assignment tracking

#### Projects
- Project portfolio overview
- Budget tracking
- Repository links
- Creation dates

#### Analytics & Insights
- Code Impact Analysis (Maker vs Mender profiles)
- Commit activity visualization
- Developer profile distribution
- Insights into team composition

#### Activity Feed
- Real-time commit activity
- Code change metrics (+/- lines)
- Author tracking
- Time-based feed

## Technology Stack

- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **React Router** - Navigation
- **Axios** - API calls
- **Recharts** - Data visualization
- **Tailwind CSS 4** - Styling
- **Lucide Icons** - Icons

## Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` to point to your backend API:
```
VITE_API_URL=http://localhost:8000
```

3. Run development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

Built files will be in `dist/` directory.

## API Integration

The UI connects to the CoreSight backend API. Key endpoints:

- **Users**: `/api/users` - User management
- **Tasks**: `/api/tasks` - Task tracking
- **Projects**: `/api/projects` - Project management
- **Analytics**: `/api/analytics` - Metrics and insights
- **Commits**: `/api/commits` - Commit activity
- **Issues**: `/api/issues` - Issue tracking

## Demo Credentials

For development/demo, any email and password will work for login. The JWT is mocked locally.

In production, connect to your backend authentication endpoint.

## Project Structure

```
src/
├── components/         # Reusable components
│   ├── AdminLayout.tsx    # Main layout with sidebar
│   └── ProtectedRoute.tsx # Auth guard
├── contexts/          # React contexts
│   └── AuthContext.tsx    # Authentication state
├── lib/              # Utilities
│   └── api.ts            # API client & endpoints
├── pages/            # Page components
│   ├── Login.tsx         # Login page
│   ├── Dashboard.tsx     # Dashboard overview
│   ├── Users.tsx         # User list
│   ├── UserForm.tsx      # Add/edit user
│   ├── Tasks.tsx         # Task tracking
│   ├── Projects.tsx      # Projects list
│   ├── Analytics.tsx     # Analytics & charts
│   └── Activity.tsx      # Activity feed
├── App.tsx           # Root component & routing
├── main.tsx          # Entry point
└── index.css         # Swiss design system styles
```

## Customization

### Updating Colors

Edit CSS variables in `src/index.css`:

```css
:root {
  --color-accent: 24 24 27;        /* Main accent color */
  --color-background: 250 250 250; /* Background */
  /* ... */
}
```

### Adding New Pages

1. Create page component in `src/pages/`
2. Add route in `src/App.tsx`
3. Add navigation item in `src/components/AdminLayout.tsx`

### Styling Components

Use utility classes matching the Swiss design system:
- `.btn` - Base button
- `.btn-primary` - Primary action
- `.card` - Content card
- `.input` - Form input
- `.badge` - Status badge
- `.table` - Data table

## License

MIT
