'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { Brain, Search, FileText, BookOpen, Settings, Home, ArrowLeft, Check } from 'lucide-react';

export type AppStep = 'welcome' | 'config' | 'query-generation' | 'query-selection' | 'search' | 'results' | 'report';

interface StepNavigationProps {
  currentStep: AppStep;
  completedSteps: AppStep[];
  onStepChange?: (step: AppStep) => void;
  canNavigateBack?: boolean;
  onBack?: () => void;
}

export function StepNavigation({
  currentStep,
  completedSteps,
  onStepChange,
  canNavigateBack = true,
  onBack
}: StepNavigationProps) {
  const steps = [
    { id: 'welcome' as const, title: 'Welcome', icon: Home, color: 'indigo' },
    { id: 'config' as const, title: 'Setup', icon: Settings, color: 'blue' },
    { id: 'query-generation' as const, title: 'Generate', icon: Brain, color: 'purple' },
    { id: 'query-selection' as const, title: 'Select', icon: Search, color: 'green' },
    { id: 'results' as const, title: 'Papers', icon: FileText, color: 'orange' },
    { id: 'report' as const, title: 'Report', icon: BookOpen, color: 'red' }
  ];

  const currentStepIndex = steps.findIndex(step => step.id === currentStep);

  return (
    <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Back Button */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                pAIper
              </span>
            </div>
            
            {canNavigateBack && currentStep !== 'welcome' && onBack && (
              <motion.button
                onClick={onBack}
                className="flex items-center space-x-1 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <ArrowLeft className="w-4 h-4" />
                <span className="text-sm font-medium">Back</span>
              </motion.button>
            )}
          </div>

          {/* Step Progress */}
          {currentStep !== 'welcome' && (
            <div className="hidden md:flex items-center space-x-1">
              {steps.slice(1).map((step, index) => {
                const isCompleted = completedSteps.includes(step.id);
                const isCurrent = step.id === currentStep;
                const isAccessible = index <= currentStepIndex - 1;
                const Icon = step.icon;

                return (
                  <div key={step.id} className="flex items-center">
                    <motion.button
                      onClick={() => isAccessible && onStepChange?.(step.id)}
                      disabled={!isAccessible}
                      className={cn(
                        "relative flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                        isCurrent && "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400",
                        isCompleted && !isCurrent && "text-green-600 dark:text-green-400 hover:bg-green-50 dark:hover:bg-green-900/20",
                        !isCompleted && !isCurrent && isAccessible && "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800/30",
                        !isAccessible && "text-gray-400 dark:text-gray-600 cursor-not-allowed"
                      )}
                      whileHover={isAccessible ? { scale: 1.02 } : {}}
                      whileTap={isAccessible ? { scale: 0.98 } : {}}
                    >
                      <div className="relative">
                        <Icon className="w-4 h-4" />
                        {isCompleted && (
                          <motion.div
                            className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full flex items-center justify-center"
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ type: "spring", stiffness: 400, damping: 20 }}
                          >
                            <Check className="w-2 h-2 text-white" />
                          </motion.div>
                        )}
                      </div>
                      <span className="hidden lg:block">{step.title}</span>
                    </motion.button>
                    
                    {index < steps.slice(1).length - 1 && (
                      <div className="w-8 h-px bg-gray-200 dark:bg-gray-700 mx-1" />
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {/* Progress Indicator for Mobile */}
          {currentStep !== 'welcome' && (
            <div className="md:hidden flex items-center space-x-2">
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Step {currentStepIndex} of {steps.length - 1}
              </div>
              <div className="w-20 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
                  initial={{ width: 0 }}
                  animate={{ width: `${(currentStepIndex / (steps.length - 1)) * 100}%` }}
                  transition={{ duration: 0.3, ease: "easeInOut" }}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Smooth page transition wrapper
interface PageTransitionProps {
  children: React.ReactNode;
  currentStep: AppStep;
}

export function PageTransition({ children, currentStep }: PageTransitionProps) {
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={currentStep}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3, ease: "easeInOut" }}
        className="flex-1"
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}