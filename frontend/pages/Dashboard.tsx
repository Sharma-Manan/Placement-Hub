import React, { useEffect } from 'react';
import Header from '../components/Header';
import { Link, useNavigate } from 'react-router-dom';


interface DashboardProps {
  toggleTheme: () => void;
  isDark: boolean;
}

const Dashboard: React.FC<DashboardProps> = ({ toggleTheme, isDark }) => {
    const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      navigate('/login');
    }
  }, [navigate]);

  return (
    <div className="relative flex min-h-screen w-full flex-col overflow-x-hidden bg-background-light dark:bg-background-dark text-[#140d1b] dark:text-white">
      <Header toggleTheme={toggleTheme} isDark={isDark} />
      
      <main className="flex flex-1 justify-center py-8">
        <div className="layout-content-container flex flex-col max-w-[1200px] flex-1 px-4 md:px-10 gap-8">
          
          {/* Welcome Hero Section */}
          <section className="flex flex-wrap justify-between items-center gap-6 p-8 rounded-xl bg-white dark:bg-[#21172b] border border-[#ede7f3] dark:border-[#2d2238] shadow-sm">
            <div className="flex flex-col gap-3 max-w-lg">
              <h1 className="text-3xl md:text-4xl font-black leading-tight tracking-[-0.033em] text-[#140d1b] dark:text-white">
                Welcome to PLACEMIND.AI
              </h1>
              <p className="text-[#734c9a] dark:text-[#a686c7] text-lg font-medium">
                Your placement journey starts here. Your profile is <span className="text-primary font-bold">80% complete</span>.
              </p>
              <div className="w-full bg-[#ede7f3] dark:bg-[#2d2238] rounded-full h-2.5 mt-2">
                <div className="bg-primary h-2.5 rounded-full" style={{ width: '80%' }}></div>
              </div>
            </div>
            <Link to="/profile" className="flex min-w-[200px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-12 px-6 bg-primary text-white text-base font-bold leading-normal tracking-wide shadow-lg shadow-primary/20 hover:scale-[1.02] transition-transform">
              <span className="material-symbols-outlined mr-2">edit_note</span>
              <span>Create / Edit Profile</span>
            </Link>
          </section>

          {/* Metric Grid */}
          <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="flex flex-col gap-2 rounded-xl p-6 bg-white dark:bg-[#21172b] border border-[#ede7f3] dark:border-[#2d2238] shadow-sm hover:border-primary/50 transition-colors group">
              <div className="flex items-center justify-between">
                <p className="text-[#734c9a] dark:text-[#a686c7] text-sm font-semibold uppercase tracking-wider">Applied Jobs</p>
                <span className="material-symbols-outlined text-primary/40 group-hover:text-primary">send</span>
              </div>
              <p className="text-[#140d1b] dark:text-white tracking-light text-3xl font-extrabold">12</p>
            </div>
            <div className="flex flex-col gap-2 rounded-xl p-6 bg-white dark:bg-[#21172b] border border-[#ede7f3] dark:border-[#2d2238] shadow-sm hover:border-primary/50 transition-colors group">
              <div className="flex items-center justify-between">
                <p className="text-[#734c9a] dark:text-[#a686c7] text-sm font-semibold uppercase tracking-wider">Shortlisted</p>
                <span className="material-symbols-outlined text-primary/40 group-hover:text-primary">verified</span>
              </div>
              <p className="text-[#140d1b] dark:text-white tracking-light text-3xl font-extrabold">4</p>
            </div>
            <div className="flex flex-col gap-2 rounded-xl p-6 bg-white dark:bg-[#21172b] border border-[#ede7f3] dark:border-[#2d2238] shadow-sm hover:border-primary/50 transition-colors group">
              <div className="flex items-center justify-between">
                <p className="text-[#734c9a] dark:text-[#a686c7] text-sm font-semibold uppercase tracking-wider">In-Progress</p>
                <span className="material-symbols-outlined text-primary/40 group-hover:text-primary">hourglass_top</span>
              </div>
              <p className="text-[#140d1b] dark:text-white tracking-light text-3xl font-extrabold">2</p>
            </div>
            <div className="flex flex-col gap-2 rounded-xl p-6 bg-white dark:bg-[#21172b] border border-[#ede7f3] dark:border-[#2d2238] shadow-sm hover:border-primary/50 transition-colors group">
              <div className="flex items-center justify-between">
                <p className="text-[#734c9a] dark:text-[#a686c7] text-sm font-semibold uppercase tracking-wider">Interviews</p>
                <span className="material-symbols-outlined text-primary/40 group-hover:text-primary">groups</span>
              </div>
              <p className="text-[#140d1b] dark:text-white tracking-light text-3xl font-extrabold">1</p>
            </div>
          </section>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Column: Progress Timeline */}
            <div className="lg:col-span-2 flex flex-col gap-6">
              <div className="rounded-xl bg-white dark:bg-[#21172b] p-6 border border-[#ede7f3] dark:border-[#2d2238] shadow-sm h-full">
                <h3 className="text-[#140d1b] dark:text-white text-xl font-bold mb-6 flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary">analytics</span>
                  Placement Progress
                </h3>
                
                <div className="relative flex flex-col gap-0">
                  {/* Step 1 */}
                  <div className="flex gap-4">
                    <div className="flex flex-col items-center">
                      <div className="flex size-10 items-center justify-center rounded-full bg-primary text-white">
                        <span className="material-symbols-outlined">check</span>
                      </div>
                      <div className="w-0.5 grow bg-primary"></div>
                    </div>
                    <div className="pb-8 pt-1">
                      <p className="text-[#140d1b] dark:text-white text-base font-bold">Profile Verification</p>
                      <p className="text-[#734c9a] dark:text-[#a686c7] text-sm">Verified by Placement Cell on Oct 24, 2023</p>
                    </div>
                  </div>
                  
                  {/* Step 2 */}
                  <div className="flex gap-4">
                    <div className="flex flex-col items-center">
                      <div className="flex size-10 items-center justify-center rounded-full bg-primary text-white">
                        <span className="material-symbols-outlined">check</span>
                      </div>
                      <div className="w-0.5 grow bg-primary"></div>
                    </div>
                    <div className="pb-8 pt-1">
                      <p className="text-[#140d1b] dark:text-white text-base font-bold">Aptitude Assessment</p>
                      <p className="text-[#734c9a] dark:text-[#a686c7] text-sm">Score: 92th Percentile. Completed on Nov 05.</p>
                    </div>
                  </div>
                  
                  {/* Step 3 */}
                  <div className="flex gap-4">
                    <div className="flex flex-col items-center">
                      <div className="flex size-10 items-center justify-center rounded-full border-2 border-primary bg-primary/10 text-primary">
                        <span className="material-symbols-outlined">pending</span>
                      </div>
                      <div className="w-0.5 grow border-l-2 border-dashed border-[#dbcfe7] dark:border-[#2d2238]"></div>
                    </div>
                    <div className="pb-8 pt-1">
                      <p className="text-[#140d1b] dark:text-white text-base font-bold">Technical Interview</p>
                      <p className="text-primary text-sm font-semibold">Scheduled: Tomorrow at 10:30 AM</p>
                    </div>
                  </div>
                  
                  {/* Step 4 */}
                  <div className="flex gap-4">
                    <div className="flex flex-col items-center">
                      <div className="flex size-10 items-center justify-center rounded-full bg-[#ede7f3] dark:bg-[#2d2238] text-[#734c9a]">
                        <span className="material-symbols-outlined">circle</span>
                      </div>
                    </div>
                    <div className="pt-1">
                      <p className="text-[#140d1b]/50 dark:text-white/50 text-base font-bold">HR Discussion</p>
                      <p className="text-[#734c9a]/50 dark:text-[#a686c7]/50 text-sm">Pending technical clearance</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column: Events & Recommendations */}
            <div className="flex flex-col gap-6">
              {/* Events Card */}
              <div className="rounded-xl bg-white dark:bg-[#21172b] p-6 border border-[#ede7f3] dark:border-[#2d2238] shadow-sm">
                <h3 className="text-[#140d1b] dark:text-white text-lg font-bold mb-4">Upcoming Events</h3>
                <div className="flex flex-col gap-4">
                  <div className="flex items-start gap-3 p-3 rounded-lg bg-background-light dark:bg-[#2d2238] border-l-4 border-primary">
                    <div className="flex flex-col items-center justify-center bg-white dark:bg-[#21172b] rounded-md px-2 py-1 min-w-[50px] shadow-sm">
                      <span className="text-[10px] font-bold uppercase text-primary">Nov</span>
                      <span className="text-lg font-black">12</span>
                    </div>
                    <div className="flex flex-col">
                      <p className="text-sm font-bold truncate">Google Cloud Info Session</p>
                      <p className="text-xs text-[#734c9a] dark:text-[#a686c7]">02:00 PM • Virtual</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-3 rounded-lg bg-background-light dark:bg-[#2d2238] border-l-4 border-slate-300">
                    <div className="flex flex-col items-center justify-center bg-white dark:bg-[#21172b] rounded-md px-2 py-1 min-w-[50px] shadow-sm">
                      <span className="text-[10px] font-bold uppercase text-slate-500">Nov</span>
                      <span className="text-lg font-black text-slate-600 dark:text-slate-400">15</span>
                    </div>
                    <div className="flex flex-col">
                      <p className="text-sm font-bold truncate">Mock Interview Workshop</p>
                      <p className="text-xs text-[#734c9a] dark:text-[#a686c7]">10:00 AM • Main Hall</p>
                    </div>
                  </div>
                </div>
                <button className="w-full mt-4 py-2 text-xs font-bold text-primary hover:underline">View All Events</button>
              </div>

              {/* Resume Tip Card */}
              <div className="rounded-xl bg-primary p-6 text-white shadow-lg relative overflow-hidden">
                <div className="relative z-10 flex flex-col gap-2">
                  <span className="material-symbols-outlined text-white/50 text-4xl mb-2">lightbulb</span>
                  <h4 className="font-bold text-lg">AI Resume Score: 85</h4>
                  <p className="text-sm text-white/80">Add more "Impact Verbs" to your project descriptions to reach 95+.</p>
                  <button className="mt-4 px-4 py-2 bg-white text-primary rounded-lg text-xs font-bold w-fit hover:bg-opacity-90 transition-all">Optimize Now</button>
                </div>
                <div className="absolute -right-4 -bottom-4 opacity-10">
                  <span className="material-symbols-outlined text-[120px]">smart_toy</span>
                </div>
              </div>
            </div>
          </div>

          {/* Recommended Jobs Section */}
          <section className="flex flex-col gap-4 pb-12">
            <div className="flex items-center justify-between px-2">
              <h2 className="text-[#140d1b] dark:text-white text-[22px] font-bold leading-tight tracking-[-0.015em]">Recommended for You</h2>
              <a href="#" className="text-primary font-bold text-sm flex items-center gap-1">Browse All <span className="material-symbols-outlined text-sm">arrow_forward</span></a>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Job Card 1 */}
              <div className="flex items-center gap-4 p-4 rounded-xl bg-white dark:bg-[#21172b] border border-[#ede7f3] dark:border-[#2d2238] shadow-sm hover:shadow-md transition-shadow">
                <div className="size-14 rounded-lg bg-slate-100 dark:bg-[#2d2238] flex items-center justify-center overflow-hidden border border-slate-200 dark:border-slate-700">
                  <span className="material-symbols-outlined text-slate-400">corporate_fare</span>
                </div>
                <div className="flex flex-col grow">
                  <h4 className="font-bold text-base">Software Engineer I</h4>
                  <p className="text-sm text-[#734c9a] dark:text-[#a686c7]">TechCorp Solutions • $85k - $110k</p>
                  <div className="flex gap-2 mt-2">
                    <span className="px-2 py-0.5 rounded bg-primary/10 text-primary text-[10px] font-bold">Python</span>
                    <span className="px-2 py-0.5 rounded bg-primary/10 text-primary text-[10px] font-bold">React</span>
                  </div>
                </div>
                <button className="px-4 py-2 border-2 border-primary text-primary hover:bg-primary hover:text-white rounded-lg text-sm font-bold transition-colors">Apply</button>
              </div>
              
              {/* Job Card 2 */}
              <div className="flex items-center gap-4 p-4 rounded-xl bg-white dark:bg-[#21172b] border border-[#ede7f3] dark:border-[#2d2238] shadow-sm hover:shadow-md transition-shadow">
                <div className="size-14 rounded-lg bg-slate-100 dark:bg-[#2d2238] flex items-center justify-center overflow-hidden border border-slate-200 dark:border-slate-700">
                  <span className="material-symbols-outlined text-slate-400">database</span>
                </div>
                <div className="flex flex-col grow">
                  <h4 className="font-bold text-base">Data Analyst Intern</h4>
                  <p className="text-sm text-[#734c9a] dark:text-[#a686c7]">Global Data Inc. • $25/hr</p>
                  <div className="flex gap-2 mt-2">
                    <span className="px-2 py-0.5 rounded bg-primary/10 text-primary text-[10px] font-bold">SQL</span>
                    <span className="px-2 py-0.5 rounded bg-primary/10 text-primary text-[10px] font-bold">Tableau</span>
                  </div>
                </div>
                <button className="px-4 py-2 border-2 border-primary text-primary hover:bg-primary hover:text-white rounded-lg text-sm font-bold transition-colors">Apply</button>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;