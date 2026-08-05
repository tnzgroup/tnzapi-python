export type NavItem = { label: string; href: string };
export type NavSection = { title: string; items: NavItem[] };

export const NAV_SECTIONS: NavSection[] = [
  {
    title: "Messaging",
    items: [
      { label: "SMS", href: "/messaging/sms" },
      { label: "Email", href: "/messaging/email" },
      { label: "Fax", href: "/messaging/fax" },
      { label: "TTS", href: "/messaging/tts" },
      { label: "Voice", href: "/messaging/voice" },
      { label: "WhatsApp", href: "/messaging/whatsapp" },
      { label: "RCS", href: "/messaging/rcs" },
      { label: "Workflow", href: "/messaging/workflow" },
    ],
  },
  {
    title: "Reports",
    items: [
      { label: "Status", href: "/reports/status" },
      { label: "SMS Reply", href: "/reports/sms-reply" },
      { label: "Received", href: "/reports/received" },
    ],
  },
  {
    title: "Actions",
    items: [
      { label: "Abort", href: "/actions/abort" },
      { label: "Reschedule", href: "/actions/reschedule" },
      { label: "Resubmit", href: "/actions/resubmit" },
      { label: "Pacing", href: "/actions/pacing" },
    ],
  },
  {
    title: "Addressbook",
    items: [
      { label: "Contacts", href: "/addressbook/contacts" },
      { label: "Groups", href: "/addressbook/groups" },
      { label: "Contact Groups", href: "/addressbook/contact-groups" },
      { label: "Group Contacts", href: "/addressbook/group-contacts" },
    ],
  },
  {
    title: "Opt-Out",
    items: [{ label: "Opt-Out List", href: "/optout" }],
  },
  {
    title: "Settings",
    items: [{ label: "General", href: "/settings" }],
  },
];