'use client';

import React, { useState, useEffect } from 'react';
import { Navbar } from '../components/Navbar';
import { DashboardTab } from '../components/DashboardTab';
import { AssistantTab } from '../components/AssistantTab';
import { PerformanceTab } from '../components/PerformanceTab';
import { PracticeTab } from '../components/PracticeTab';
import { AssessmentsTab } from '../components/AssessmentsTab';
import { StudyCoachTab } from '../components/StudyCoachTab';
import { AuditTab } from '../components/AuditTab';
import {
  fetchApi,
  DemoStudent,
  StudentProfile,
  CourseSummary,
  PerformanceSummary,
  StudyRecommendation,
} from '../lib/api';

const DEFAULT_DEMO_STUDENTS: DemoStudent[] = [
  {
    student_id: '02754054-361a-4025-be96-1bd8a049ae18',
    name: 'Aarav Sharma',
    profile_description: 'CS Senior — Aptitude & Python Focus',
    courses_count: 11,
    assessments_count: 9,
    views: 11,
  },
  {
    student_id: '073df96e-ade7-40fe-ba34-5e2f8e272845',
    name: 'Priya Patel',
    profile_description: 'Data Science & Technical Hackathon',
    courses_count: 16,
    assessments_count: 10,
    views: 16,
  },
  {
    student_id: '05c950e8-30fe-4d30-bf11-97b4e1b85ae0',
    name: 'Rohan Verma',
    profile_description: 'Business Analytics & Machine Learning',
    courses_count: 21,
    assessments_count: 10,
    views: 21,
  },
  {
    student_id: '07909202-7d6c-4dcb-bb9d-101c4d619140',
    name: 'Ananya Reddy',
    profile_description: 'Full Stack Developer & Java',
    courses_count: 12,
    assessments_count: 10,
    views: 12,
  },
];

export default function Home() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [practiceTopic, setPracticeTopic] = useState<string>('Profit and Loss');
  const [demoStudents, setDemoStudents] = useState<DemoStudent[]>(DEFAULT_DEMO_STUDENTS);
  const [activeStudentId, setActiveStudentId] = useState<string>('02754054-361a-4025-be96-1bd8a049ae18');

  // Loaded data for active student
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [courses, setCourses] = useState<CourseSummary[]>([]);
  const [performance, setPerformance] = useState<PerformanceSummary | null>(null);
  const [recommendation, setRecommendation] = useState<StudyRecommendation | null>(null);
  const [assessmentHistory, setAssessmentHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Load demo students list on mount
  useEffect(() => {
    async function loadDemoList() {
      try {
        const list = await fetchApi<DemoStudent[]>('/students/demo-list', activeStudentId);
        if (list && list.length > 0) {
          setDemoStudents(list);
        }
      } catch (err) {
        console.warn('Using default demo student list');
      }
    }
    loadDemoList();
  }, []);

  // Reload student data when active student changes
  useEffect(() => {
    async function loadStudentData() {
      setLoading(true);
      try {
        const [profData, coursesData, perfData, recData, histData] = await Promise.all([
          fetchApi<StudentProfile>('/students/me/profile', activeStudentId).catch(() => null),
          fetchApi<CourseSummary[]>('/students/me/courses', activeStudentId).catch(() => []),
          fetchApi<PerformanceSummary>('/performance/me', activeStudentId).catch(() => null),
          fetchApi<StudyRecommendation>('/performance/me/recommendation', activeStudentId).catch(() => null),
          fetchApi<any[]>('/students/me/assessments/history', activeStudentId).catch(() => []),
        ]);

        setProfile(profData);
        setCourses(coursesData);
        setPerformance(perfData);
        setRecommendation(recData);
        setAssessmentHistory(histData);
      } catch (err) {
        console.error('Failed to load student data:', err);
      } finally {
        setLoading(false);
      }
    }

    loadStudentData();
  }, [activeStudentId]);

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
      {/* Navbar with Student Switcher */}
      <Navbar
        demoStudents={demoStudents}
        activeStudentId={activeStudentId}
        onSelectStudent={(id) => setActiveStudentId(id)}
        activeTab={activeTab}
        onSelectTab={(tab) => setActiveTab(tab)}
      />

      {/* Main Tab Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {loading && !profile ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <div className="w-10 h-10 border-4 border-sky-600 border-t-transparent rounded-full animate-spin mb-4" />
            <p className="text-sm text-slate-500 font-medium">Loading student records and analytics...</p>
          </div>
        ) : (
          <>
            {activeTab === 'dashboard' && (
              <DashboardTab
                profile={profile}
                courses={courses}
                performance={performance}
                recommendation={recommendation}
                onNavigateTab={(tab) => setActiveTab(tab)}
              />
            )}

            {activeTab === 'assistant' && <AssistantTab studentId={activeStudentId} />}

            {activeTab === 'performance' && (
              <PerformanceTab
                performance={performance}
                assessmentHistory={assessmentHistory}
              />
            )}

            {activeTab === 'practice' && (
              <PracticeTab
                studentId={activeStudentId}
                initialTopic={practiceTopic}
              />
            )}

            {activeTab === 'assessments' && <AssessmentsTab studentId={activeStudentId} />}

            {activeTab === 'study-coach' && (
              <StudyCoachTab
                recommendation={recommendation}
                onStartPractice={(targetTopic) => {
                  setPracticeTopic(targetTopic);
                  setActiveTab('practice');
                }}
              />
            )}

            {activeTab === 'audit' && <AuditTab studentId={activeStudentId} />}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-4 text-center text-xs text-slate-400">
        AI College Learning Assistant • Production-Grade Prototype • Powered by FastAPI & Next.js
      </footer>
    </div>
  );
}
