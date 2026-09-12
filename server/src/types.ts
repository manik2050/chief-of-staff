export type PriorityStatus = "on_track" | "at_risk" | "blocked" | "done";

export interface Priority {
  id: string;
  title: string;
  owner: string;
  status: PriorityStatus;
  due: string;
  impact: "high" | "medium" | "low";
}

export interface Meeting {
  id: string;
  time: string;
  title: string;
  attendees: string[];
  location: string;
}

export interface TeamMember {
  id: string;
  name: string;
  role: string;
  availability: "available" | "focus" | "ooo";
  workload: number;
}

export interface Update {
  id: string;
  author: string;
  text: string;
  at: string;
}

export interface Stat {
  label: string;
  value: string;
  delta: number;
  hint: string;
}

export interface Overview {
  stats: Stat[];
  priorities: Priority[];
  meetings: Meeting[];
  team: TeamMember[];
  updates: Update[];
}
