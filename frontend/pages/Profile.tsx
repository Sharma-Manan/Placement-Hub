import React, { useState } from 'react';
import Header from '../components/Header';
import { apiRequest } from '../services/api';


interface ProfileProps {
  toggleTheme: () => void;
  isDark: boolean;
}

const Profile: React.FC<ProfileProps> = ({ toggleTheme, isDark }) => {
    const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [rollNo, setRollNo] = useState('');
  const [departmentId, setDepartmentId] = useState('');
  const [graduationYear, setGraduationYear] = useState('');
  const [cgpa, setCgpa] = useState('');
  const [activeBacklogs, setActiveBacklogs] = useState('');
  const [totalBacklogs, setTotalBacklogs] = useState("");
  const [tenthPercentage, setTenthPercentage] = useState("");
  const [twelfthPercentage, setTwelfthPercentage] = useState("");
  const [resumeUrl, setResumeUrl] = useState('');
  const [linkedinUrl, setLinkedinUrl] = useState('');
  const [githubUrl, setGithubUrl] = useState('');
  const [portfolioUrl, setPortfolioUrl] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');


  const handleSaveProfile = async () => {
  setError('');
  setSuccess('');

  try {
    await apiRequest('/student/profile', {
      method: 'POST',
      body: JSON.stringify({
        first_name: firstName,
    last_name: lastName,

    roll_no: rollNo,                    
    department_id: departmentId,
    graduation_year: Number(graduationYear),
    cgpa: Number(cgpa),

    tenth_percentage: Number(tenthPercentage),
    twelfth_percentage: Number(twelfthPercentage),

    active_backlogs: Number(activeBacklogs),
    total_backlogs: Number(totalBacklogs),   

    resume_url: resumeUrl || "https://example.com",
    linkedin_url: linkedinUrl || "https://linkedin.com",
    github_url: githubUrl || "https://github.com",
    portfolio_url: portfolioUrl || "https://example.com",

    placement_status: "unplaced",
    is_profile_complete: true,
      }),
    });

    setSuccess('Profile saved successfully');
  } catch (err: any) {
    setError(err.message || 'Failed to save profile');
  }
};


  return (
    <div className="bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-100 font-display min-h-screen flex flex-col">
      <Header toggleTheme={toggleTheme} isDark={isDark} />

      <main className="flex-1 px-4 md:px-10 lg:px-40 py-8">
        {/* Page Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
          <div className="flex flex-col gap-1">
            <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">Student Profile</h1>
            <p className="text-slate-500 dark:text-slate-400 text-base">Complete your profile to increase your chances of getting placed.</p>
          </div>
          <div className="flex gap-3">
            <button className="flex items-center justify-center rounded-lg h-10 px-4 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-sm font-bold hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
              <span className="truncate">Preview Public Profile</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Sidebar (Nav) */}
          <aside className="lg:col-span-3">
            <div className="flex flex-col gap-1 sticky top-24">
              <a href="#" className="flex items-center gap-3 px-4 py-3 rounded-xl bg-primary text-white shadow-md shadow-primary/20">
                <span className="material-symbols-outlined text-lg">person</span>
                <span className="font-bold text-sm">General Info</span>
              </a>
              <a href="#" className="flex items-center gap-3 px-4 py-3 rounded-xl text-slate-600 dark:text-slate-400 hover:bg-white dark:hover:bg-slate-800 transition-all">
                <span className="material-symbols-outlined text-lg">description</span>
                <span className="font-medium text-sm">Resumes</span>
              </a>
              <a href="#" className="flex items-center gap-3 px-4 py-3 rounded-xl text-slate-600 dark:text-slate-400 hover:bg-white dark:hover:bg-slate-800 transition-all">
                <span className="material-symbols-outlined text-lg">workspace_premium</span>
                <span className="font-medium text-sm">Certifications</span>
              </a>
              <a href="#" className="flex items-center gap-3 px-4 py-3 rounded-xl text-slate-600 dark:text-slate-400 hover:bg-white dark:hover:bg-slate-800 transition-all">
                <span className="material-symbols-outlined text-lg">history_edu</span>
                <span className="font-medium text-sm">Internships</span>
              </a>
            </div>
          </aside>

          {/* Main Form Section */}
          <div className="lg:col-span-9 flex flex-col gap-8">
            {/* Academic Information Section */}
            <section className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
              <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex items-center gap-3">
                <span className="material-symbols-outlined text-primary">school</span>
                <h2 className="text-lg font-bold text-slate-900 dark:text-white">Academic Information</h2>
              </div>
              <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="flex flex-col gap-2">
                  <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">First Name</label>
                  <input type="text" value={firstName} onChange={(e) => setFirstName(e.target.value)} placeholder="e.g. Alex" className="form-input rounded-lg border-slate-300 dark:border-slate-700 dark:bg-slate-800 text-slate-900 dark:text-white focus:border-primary focus:ring-primary h-12 px-4 w-full" />
                </div>
                <div className="flex flex-col gap-2">
                  <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Last Name</label>
                  <input type="text" value={lastName} onChange={(e) => setLastName(e.target.value)} placeholder="e.g. Rivera" className="form-input rounded-lg border-slate-300 dark:border-slate-700 dark:bg-slate-800 text-slate-900 dark:text-white focus:border-primary focus:ring-primary h-12 px-4 w-full" />
                </div>
                <div className="flex flex-col gap-2">
                  <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Roll Number</label>
                  <input type="text" value={rollNo} onChange={(e) => setRollNo(e.target.value)} placeholder="Enter Roll Number" className="form-input rounded-lg border-slate-300 dark:border-slate-700 dark:bg-slate-800 text-slate-900 dark:text-white focus:border-primary focus:ring-primary h-12 px-4 w-full" />
                </div>
                <div className="flex flex-col gap-2">
                  <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Department</label>
                  <select
                    value={departmentId}
                    onChange={(e) => setDepartmentId(e.target.value)}
                  >     
                    <option value="it">Information Technology</option>
                    <option value="cse">Computer Science</option>
                    <option value="mech">Mechanical</option>
                  </select>

                </div>
                <div className="flex flex-col gap-2">
                  <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Graduation Year</label>
                  <select value={graduationYear} onChange={(e) => setGraduationYear(e.target.value)} className="form-select rounded-lg border-slate-300 dark:border-slate-700 dark:bg-slate-800 text-slate-900 dark:text-white focus:border-primary focus:ring-primary h-12 px-4 w-full">
                    <option value="2024">2024</option>
                    <option value="2025">2025</option>
                    <option value="2026">2026</option>
                  </select>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex flex-col gap-2">
                    <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">CGPA</label>
                    <input type="number" step="0.01" max="10" value={cgpa} onChange={(e) => setCgpa(e.target.value)} placeholder="0.00" className="form-input rounded-lg border-slate-300 dark:border-slate-700 dark:bg-slate-800 text-slate-900 dark:text-white focus:border-primary focus:ring-primary h-12 px-4 w-full" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">
                    10th Percentage
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      value={tenthPercentage}
                      onChange={(e) => setTenthPercentage(e.target.value)}
                      className="w-full rounded border px-3 py-2"
                      placeholder="e.g. 85.40"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">
                      12th Percentage
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      value={twelfthPercentage}
                      onChange={(e) => setTwelfthPercentage(e.target.value)}
                      className="w-full rounded border px-3 py-2"
                      placeholder="e.g. 78.20"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">
                      Total Backlogs
                    </label>
                    <input
                      type="number"
                      value={totalBacklogs}
                      onChange={(e) => setTotalBacklogs(e.target.value)}
                      className="w-full rounded border px-3 py-2"
                      placeholder="0"
                    />
                  </div>
                  <div className="flex flex-col gap-2">
                    <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Active Backlogs</label>
                    <input type="number" value={activeBacklogs} onChange={(e) => setActiveBacklogs(e.target.value)} placeholder="0" className="form-input rounded-lg border-slate-300 dark:border-slate-700 dark:bg-slate-800 text-slate-900 dark:text-white focus:border-primary focus:ring-primary h-12 px-4 w-full" />
                  </div>
                </div>
              </div>
            </section>

            {/* Professional Links Section */}
            <section className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
              <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex items-center gap-3">
                <span className="material-symbols-outlined text-primary">link</span>
                <h2 className="text-lg font-bold text-slate-900 dark:text-white">Professional Presence</h2>
              </div>
              <div className="p-6 flex flex-col gap-6">
                <div className="flex flex-col gap-2">
                  <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Resume URL</label>
                  <div className="relative flex items-center">
                    <span className="material-symbols-outlined absolute left-4 text-slate-400">description</span>
                    <input type="url" value={resumeUrl} onChange={(e) => setResumeUrl(e.target.value)} placeholder="https://drive.google.com/your-resume" className="form-input w-full rounded-lg border-slate-300 dark:border-slate-700 dark:bg-slate-800 text-slate-900 dark:text-white focus:border-primary focus:ring-primary h-12 pl-12 pr-4" />
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="flex flex-col gap-2">
                    <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">LinkedIn Profile</label>
                    <div className="relative flex items-center">
                      <span className="material-symbols-outlined absolute left-4 text-slate-400">share</span>
                      <input type="url" value={linkedinUrl} onChange={(e) => setLinkedinUrl(e.target.value)} placeholder="linkedin.com/in/username" className="form-input w-full rounded-lg border-slate-300 dark:border-slate-700 dark:bg-slate-800 text-slate-900 dark:text-white focus:border-primary focus:ring-primary h-12 pl-12 pr-4" />
                    </div>
                  </div>
                  <div className="flex flex-col gap-2">
                    <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">GitHub Profile</label>
                    <div className="relative flex items-center">
                      <span className="material-symbols-outlined absolute left-4 text-slate-400">code</span>
                      <input type="url" value={githubUrl} onChange={(e) => setGithubUrl(e.target.value)} placeholder="github.com/username" className="form-input w-full rounded-lg border-slate-300 dark:border-slate-700 dark:bg-slate-800 text-slate-900 dark:text-white focus:border-primary focus:ring-primary h-12 pl-12 pr-4" />
                    </div>
                  </div>
                </div>
                <div className="flex flex-col gap-2">
                  <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">Personal Portfolio</label>
                  <div className="relative flex items-center">
                    <span className="material-symbols-outlined absolute left-4 text-slate-400">language</span>
                    <input type="url" value={portfolioUrl} onChange={(e) => setPortfolioUrl(e.target.value)} placeholder="www.yourname.dev" className="form-input w-full rounded-lg border-slate-300 dark:border-slate-700 dark:bg-slate-800 text-slate-900 dark:text-white focus:border-primary focus:ring-primary h-12 pl-12 pr-4" />
                  </div>
                </div>
              </div>
            </section>

            {/* Form Footer */}
            <div className="flex items-center justify-end gap-4 pb-12">
              <button className="px-6 h-12 rounded-xl text-slate-600 dark:text-slate-400 font-bold hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                Cancel
              </button>
              <button
                onClick={handleSaveProfile}
                className="px-10 h-12 rounded-xl bg-primary text-white font-bold shadow-lg shadow-primary/30 hover:bg-primary/90 transition-all flex items-center gap-2"
              >
                <span className="material-symbols-outlined">save</span>
                Save Profile
              </button>
              {error && <p className="text-red-500 mt-2">{error}</p>}
              {success && <p className="text-green-600 mt-2">{success}</p>}

            </div>
          </div>
        </div>
      </main>

      {/* Bottom Info Banner */}
      <footer className="bg-primary/5 dark:bg-slate-950 px-10 py-6 border-t border-slate-200 dark:border-slate-800 mt-auto">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-primary">verified</span>
            <p className="text-sm text-slate-600 dark:text-slate-400">All data is securely encrypted and shared only with verified campus recruiters.</p>
          </div>
          <p className="text-xs text-slate-400">© 2024 PLACEMIND.AI Placement Management System. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default Profile;