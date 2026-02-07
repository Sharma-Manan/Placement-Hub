import React, { useState } from 'react';
import { apiRequest } from '../services/api';
import { Link, useNavigate } from 'react-router-dom';

const Register: React.FC = () => {
  const navigate = useNavigate();

  // ===== State =====
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  // ===== Register Handler =====
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const res = await apiRequest<{
        access_token: string;
        refresh_token: string;
      }>('/auth/register', {
        method: 'POST',
        body: JSON.stringify({
          email,
          password,
          role: 'student',
          first_name: firstName,
          last_name: lastName,
        }),
      });

      localStorage.setItem('access_token', res.access_token);
      localStorage.setItem('refresh_token', res.refresh_token);

      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Registration failed');
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-white dark:bg-[#191022]">
      <main className="flex-1 flex items-center justify-center px-4">
        <div className="w-full max-w-md bg-white dark:bg-[#251a33] rounded-xl shadow-lg p-8">
          <h1 className="text-3xl font-extrabold text-center mb-2">
            Create Student Account
          </h1>
          <p className="text-center text-gray-500 mb-8">
            Join PLACEMIND.AI to manage your college placements and career opportunities.
          </p>

          <form onSubmit={handleRegister} className="space-y-5">
            {error && (
              <p className="text-red-500 text-sm text-center">{error}</p>
            )}

            {/* First Name */}
            <div>
              <label className="block text-sm font-semibold mb-1">
                First Name
              </label>
              <input
                type="text"
                required
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="w-full border rounded-lg px-4 py-3"
                placeholder="Enter first name"
              />
            </div>

            {/* Last Name */}
            <div>
              <label className="block text-sm font-semibold mb-1">
                Last Name
              </label>
              <input
                type="text"
                required
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className="w-full border rounded-lg px-4 py-3"
                placeholder="Enter last name"
              />
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-semibold mb-1">
                College Email Address
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full border rounded-lg px-4 py-3"
                placeholder="e.g. name@university.edu"
              />
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-semibold mb-1">
                Password
              </label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full border rounded-lg px-4 py-3"
                placeholder="Create a strong password"
              />
            </div>

            {/* Role (Read-only) */}
            <div>
              <label className="block text-sm font-semibold mb-1">
                Account Role
              </label>
              <div className="w-full border border-dashed rounded-lg px-4 py-3 text-purple-600 font-semibold flex items-center justify-between">
                STUDENT
                <span className="text-xs opacity-50">Locked</span>
              </div>
            </div>

            <button
              type="submit"
              className="w-full bg-purple-600 text-white font-bold py-3 rounded-lg hover:bg-purple-700 transition"
            >
              Create Account →
            </button>

            <p className="text-xs text-center text-gray-500 mt-4">
              By clicking "Create Account", you agree to our{' '}
              <span className="text-purple-600 font-semibold cursor-pointer">
                Terms of Service
              </span>{' '}
              and{' '}
              <span className="text-purple-600 font-semibold cursor-pointer">
                Privacy Policy
              </span>.
            </p>
          </form>

          <p className="text-center text-sm mt-6">
            Already have an account?{' '}
            <Link to="/login" className="text-purple-600 font-bold">
              Log in here
            </Link>
          </p>
        </div>
      </main>
    </div>
  );
};

export default Register;
