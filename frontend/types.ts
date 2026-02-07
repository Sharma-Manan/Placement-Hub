export interface User {
  name: string;
  email: string;
  role: 'student' | 'admin';
  avatarUrl?: string;
}

export interface Job {
  id: string;
  title: string;
  company: string;
  salary: string;
  tags: string[];
}
