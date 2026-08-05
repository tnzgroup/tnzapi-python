import { lazy, Suspense, type ReactNode } from 'react'
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom'
import { Sidebar } from '@/components/layout/Sidebar'
import { NAV_SECTIONS } from '@/components/layout/nav-items'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import HomePage from '@/pages/HomePage'
import ComingSoonPage from '@/pages/ComingSoonPage'

// Route-based code splitting — each page (and whatever it pulls in, e.g. TipTap for EmailPage's
// HtmlEditor) only downloads when its route is actually visited, instead of all 20 pages landing in
// one ~800KB main chunk regardless of which single page a visitor opens.
const SmsPage = lazy(() => import('@/pages/messaging/SmsPage'))
const EmailPage = lazy(() => import('@/pages/messaging/EmailPage'))
const FaxPage = lazy(() => import('@/pages/messaging/FaxPage'))
const TtsPage = lazy(() => import('@/pages/messaging/TtsPage'))
const VoicePage = lazy(() => import('@/pages/messaging/VoicePage'))
const WhatsAppPage = lazy(() => import('@/pages/messaging/WhatsAppPage'))
const RcsPage = lazy(() => import('@/pages/messaging/RcsPage'))
const WorkflowPage = lazy(() => import('@/pages/messaging/WorkflowPage'))
const StatusPage = lazy(() => import('@/pages/reports/StatusPage'))
const SmsReplyPage = lazy(() => import('@/pages/reports/SmsReplyPage'))
const ReceivedPage = lazy(() => import('@/pages/reports/ReceivedPage'))
const AbortPage = lazy(() => import('@/pages/actions/AbortPage'))
const ReschedulePage = lazy(() => import('@/pages/actions/ReschedulePage'))
const ResubmitPage = lazy(() => import('@/pages/actions/ResubmitPage'))
const PacingPage = lazy(() => import('@/pages/actions/PacingPage'))
const ContactsPage = lazy(() => import('@/pages/addressbook/ContactsPage'))
const GroupsPage = lazy(() => import('@/pages/addressbook/GroupsPage'))
const ContactGroupsPage = lazy(() => import('@/pages/addressbook/ContactGroupsPage'))
const GroupContactsPage = lazy(() => import('@/pages/addressbook/GroupContactsPage'))
const OptOutPage = lazy(() => import('@/pages/OptOutPage'))
const SettingsPage = lazy(() => import('@/pages/SettingsPage'))

const allNavItems = NAV_SECTIONS.flatMap((section) => section.items)

const IMPLEMENTED_ROUTES: Record<string, ReactNode> = {
  '/messaging/sms': <SmsPage />,
  '/messaging/email': <EmailPage />,
  '/messaging/fax': <FaxPage />,
  '/messaging/tts': <TtsPage />,
  '/messaging/voice': <VoicePage />,
  '/messaging/whatsapp': <WhatsAppPage />,
  '/messaging/rcs': <RcsPage />,
  '/messaging/workflow': <WorkflowPage />,
  '/reports/status': <StatusPage />,
  '/reports/sms-reply': <SmsReplyPage />,
  '/reports/received': <ReceivedPage />,
  '/actions/abort': <AbortPage />,
  '/actions/reschedule': <ReschedulePage />,
  '/actions/resubmit': <ResubmitPage />,
  '/actions/pacing': <PacingPage />,
  '/addressbook/contacts': <ContactsPage />,
  '/addressbook/groups': <GroupsPage />,
  '/addressbook/contact-groups': <ContactGroupsPage />,
  '/addressbook/group-contacts': <GroupContactsPage />,
  '/optout': <OptOutPage />,
  '/settings': <SettingsPage />,
}

function AppRoutes() {
  const location = useLocation()
  return (
    // Keyed by pathname so navigating to a different page remounts the boundary and clears any
    // error state from the previous page — without this, one page throwing would strand the user
    // on the error view with no way back in, since ErrorBoundary itself never re-renders children
    // again once it has caught an error.
    <ErrorBoundary key={location.pathname}>
      <Suspense fallback={<div className="text-sm text-muted-foreground">Loading...</div>}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          {allNavItems.map((item) => (
            <Route
              key={item.href}
              path={item.href}
              element={IMPLEMENTED_ROUTES[item.href] ?? <ComingSoonPage title={item.label} />}
            />
          ))}
        </Routes>
      </Suspense>
    </ErrorBoundary>
  )
}

function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="flex-1 p-6">
          <AppRoutes />
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App