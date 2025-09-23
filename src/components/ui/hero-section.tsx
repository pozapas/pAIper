import React from 'react'
import Link from 'next/link'
import { ArrowRight, ChevronRight, Menu, X, Brain, Search, BookOpen, Sparkles, Target, Zap } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { AnimatedGroup } from '@/components/ui/animated-group'
import { AboutSection } from '@/components/AboutSection'
import { LavaLamp } from '@/components/ui/fluid-blob'
import { cn } from '@/lib/utils'

interface HeroSectionProps {
  onStartResearch: () => void;
}

export function HeroSection({ onStartResearch }: HeroSectionProps) {
    return (
        <>
            <HeroHeader onStartResearch={onStartResearch} />
            <main className="overflow-hidden">
                <div
                    aria-hidden
                    className="z-[2] absolute inset-0 pointer-events-none isolate opacity-30 contain-strict hidden lg:block">
                    <div className="w-[35rem] h-[80rem] -translate-y-[350px] absolute left-0 top-0 -rotate-45 rounded-full bg-[radial-gradient(68.54%_68.72%_at_55.02%_31.46%,hsla(220,100%,70%,.08)_0,hsla(220,100%,55%,.02)_50%,hsla(220,100%,45%,0)_80%)]" />
                    <div className="h-[80rem] absolute right-0 top-0 w-56 rotate-45 rounded-full bg-[radial-gradient(50%_50%_at_50%_50%,hsla(260,100%,70%,.06)_0,hsla(260,100%,45%,.02)_80%,transparent_100%)] [translate:-5%_-30%]" />
                    <div className="h-[80rem] -translate-y-[200px] absolute left-1/2 top-0 w-96 rounded-full bg-[radial-gradient(50%_50%_at_50%_50%,hsla(200,100%,70%,.04)_0,hsla(200,100%,45%,.02)_80%,transparent_100%)]" />
                </div>
                
                <section>
                    <div className="relative pt-24 md:pt-36">
                        {/* Fluid blob background */}
                        <div className="absolute inset-0 -z-30 overflow-hidden">
                            <LavaLamp />
                        </div>
                        
                        <AnimatedGroup
                            variants={{
                                container: {
                                    visible: {
                                        transition: {
                                            delayChildren: 1,
                                        },
                                    },
                                },
                                item: {
                                    hidden: {
                                        opacity: 0,
                                        y: 20,
                                    },
                                    visible: {
                                        opacity: 1,
                                        y: 0,
                                        transition: {
                                            type: 'spring',
                                            bounce: 0.3,
                                            duration: 2,
                                        },
                                    },
                                },
                            }}
                            className="absolute inset-0 -z-20">
                            <div className="absolute inset-x-0 top-56 -z-20 hidden lg:top-32 dark:block bg-gradient-to-b from-blue-900/20 via-purple-900/10 to-transparent h-[800px] w-full" />
                        </AnimatedGroup>
                        
                        <div aria-hidden className="absolute inset-0 -z-10 size-full [background:radial-gradient(125%_125%_at_50%_100%,transparent_0%,var(--background)_75%)]" />
                        
                        <div className="mx-auto max-w-7xl px-6">
                            <div className="text-center sm:mx-auto lg:mr-auto lg:mt-0">
                                <AnimatedGroup preset="blur-slide">
                                    <Link
                                        href="#features"
                                        className="hover:bg-background glass group mx-auto flex w-fit items-center gap-4 rounded-full border border-primary/20 p-1 pl-4 shadow-modern transition-all duration-300 hover:shadow-modern-lg">
                                        <span className="text-foreground text-sm font-medium">✨ Open Source Research Tool</span>
                                        <span className="dark:border-background block h-4 w-0.5 border-l bg-primary/30"></span>

                                        <div className="bg-gradient-primary group-hover:bg-muted size-6 overflow-hidden rounded-full duration-500">
                                            <div className="flex w-12 -translate-x-1/2 duration-500 ease-in-out group-hover:translate-x-0">
                                                <span className="flex size-6">
                                                    <ArrowRight className="m-auto size-3 text-white" />
                                                </span>
                                                <span className="flex size-6">
                                                    <ArrowRight className="m-auto size-3 text-white" />
                                                </span>
                                            </div>
                                        </div>
                                    </Link>
                        
                                    <h1 className="mt-8 max-w-4xl mx-auto text-balance text-6xl md:text-7xl lg:mt-16 xl:text-[5.25rem] font-bold gradient-text">
                                        Find Research Papers in Minutes, Not Hours
                                    </h1>
                                    <p className="mx-auto mt-8 max-w-2xl text-balance text-xl text-muted-foreground leading-relaxed">
                                        An open-source tool that helps researchers and students find relevant academic papers quickly using AI-powered search and intelligent query generation.
                                    </p>
                                </AnimatedGroup>

                                <AnimatedGroup preset="scale" className="mt-12 flex flex-col items-center justify-center gap-4 md:flex-row">
                                    <div className="bg-gradient-primary rounded-2xl p-0.5 shadow-modern-lg">
                                        <Button
                                            onClick={onStartResearch}
                                            size="lg"
                                            className="rounded-xl px-8 py-4 text-lg bg-white text-primary hover:bg-gray-50 font-semibold shadow-none transition-all duration-200 hover:scale-105">
                                            <Sparkles className="w-5 h-5 mr-2" />
                                            <span className="text-nowrap">Try pAIper</span>
                                        </Button>
                                    </div>
                                    <Button
                                        asChild
                                        size="lg"
                                        variant="ghost"
                                        className="h-12 rounded-xl px-8 hover:bg-muted/50 text-lg font-medium">
                                        <Link href="#features">
                                            <span className="text-nowrap">See How It Works</span>
                                            <ArrowRight className="w-4 h-4 ml-2" />
                                        </Link>
                                    </Button>
                                </AnimatedGroup>
                            </div>
                        </div>

                        {/* Features Preview */}
                        <AnimatedGroup preset="slide" className="mt-16 md:mt-24">
                            <div className="mx-auto max-w-5xl px-6">
                                <div className="grid md:grid-cols-3 gap-8">
                                    <div className="glass rounded-3xl p-8 shadow-modern-lg hover:shadow-modern-xl transition-all duration-300 group hover:-translate-y-2">
                                        <div className="w-14 h-14 gradient-primary rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                                            <Zap className="w-7 h-7 text-white" />
                                        </div>
                                        <h3 className="text-xl font-bold text-foreground mb-3">Instant Smart Search</h3>
                                        <p className="text-muted-foreground leading-relaxed">
                                            Just describe your research topic in plain English. The AI creates optimized search queries to find papers you'd never discover manually.
                                        </p>
                                    </div>

                                    <div className="glass rounded-3xl p-8 shadow-modern-lg hover:shadow-modern-xl transition-all duration-300 group hover:-translate-y-2">
                                        <div className="w-14 h-14 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                                            <Target className="w-7 h-7 text-white" />
                                        </div>
                                        <h3 className="text-xl font-bold text-foreground mb-3">Multi-Source Discovery</h3>
                                        <p className="text-muted-foreground leading-relaxed">
                                            Search across Google Scholar, Scopus, and academic databases simultaneously. No more switching between platforms.
                                        </p>
                                    </div>

                                    <div className="glass rounded-3xl p-8 shadow-modern-lg hover:shadow-modern-xl transition-all duration-300 group hover:-translate-y-2">
                                        <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                                            <BookOpen className="w-7 h-7 text-white" />
                                        </div>
                                        <h3 className="text-xl font-bold text-foreground mb-3">Instant Literature Review</h3>
                                        <p className="text-muted-foreground leading-relaxed">
                                            Get research summaries, key findings, and properly formatted citations ready for your papers.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </AnimatedGroup>
                    </div>
                </section>

                {/* Academic Partners Section */}
                <section id="features" className="bg-gradient-to-br from-background via-muted/30 to-background pb-16 pt-16 md:pb-24 md:pt-24">
                    <div className="group relative m-auto max-w-5xl px-6">
                        <div className="text-center mb-16">
                            <div className="inline-block p-4 rounded-2xl bg-primary/10 mb-6">
                                <Brain className="w-8 h-8 text-primary mx-auto" />
                            </div>
                            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-6 gradient-text">
                                Used by Researchers Worldwide
                            </h2>
                            <p className="text-muted-foreground max-w-3xl mx-auto text-lg leading-relaxed">
                                An open-source project helping students, researchers, and academics discover relevant literature more efficiently.
                            </p>
                        </div>
                        
                        <div className="mx-auto mt-12 grid max-w-5xl grid-cols-2 md:grid-cols-4 gap-12 items-center">
                            <div className="flex items-center justify-center opacity-60 hover:opacity-100 transition-all duration-300 hover:scale-110">
                                <div className="text-center p-6 rounded-2xl hover:bg-muted/30 transition-colors">
                                    <Search className="w-10 h-10 mx-auto mb-3 text-muted-foreground" />
                                    <span className="text-sm font-semibold text-foreground">Google Scholar</span>
                                </div>
                            </div>

                            <div className="flex items-center justify-center opacity-60 hover:opacity-100 transition-all duration-300 hover:scale-110">
                                <div className="text-center p-6 rounded-2xl hover:bg-muted/30 transition-colors">
                                    <BookOpen className="w-10 h-10 mx-auto mb-3 text-muted-foreground" />
                                    <span className="text-sm font-semibold text-foreground">Scopus</span>
                                </div>
                            </div>

                            <div className="flex items-center justify-center opacity-60 hover:opacity-100 transition-all duration-300 hover:scale-110">
                                <div className="text-center p-6 rounded-2xl hover:bg-muted/30 transition-colors">
                                    <Brain className="w-10 h-10 mx-auto mb-3 text-muted-foreground" />
                                    <span className="text-sm font-semibold text-foreground">OpenAI</span>
                                </div>
                            </div>

                            <div className="flex items-center justify-center opacity-60 hover:opacity-100 transition-all duration-300 hover:scale-110">
                                <div className="text-center p-6 rounded-2xl hover:bg-muted/30 transition-colors">
                                    <Zap className="w-10 h-10 mx-auto mb-3 text-muted-foreground" />
                                    <span className="text-sm font-semibold text-foreground">Ollama</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* About Section */}
                <AboutSection />
            </main>
        </>
    )
}

const menuItems = [
    { name: 'Features', href: '#features' },
    { name: 'About', href: '#about' },
    { name: 'GitHub', href: 'https://github.com/pozapas' },
    { name: 'Contact', href: '#contact' },
]

interface HeroHeaderProps {
  onStartResearch: () => void;
}

const HeroHeader = ({ onStartResearch }: HeroHeaderProps) => {
    const [menuState, setMenuState] = React.useState(false)
    const [isScrolled, setIsScrolled] = React.useState(false)

    React.useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 50)
        }
        window.addEventListener('scroll', handleScroll)
        return () => window.removeEventListener('scroll', handleScroll)
    }, [])
    
    return (
        <header>
            <nav
                data-state={menuState && 'active'}
                className="fixed z-20 w-full px-2 group">
                <div className={cn('mx-auto mt-2 max-w-6xl px-6 transition-all duration-300 lg:px-12', isScrolled && 'bg-background/80 max-w-4xl rounded-2xl border backdrop-blur-xl lg:px-5 shadow-lg')}>
                    <div className="relative flex flex-wrap items-center justify-between gap-6 py-3 lg:gap-0 lg:py-4">
                        <div className="flex w-full justify-between lg:w-auto">
                            <Link
                                href="/"
                                aria-label="home"
                                className="flex items-center space-x-2">
                                <PaiperLogo />
                            </Link>

                            <button
                                onClick={() => setMenuState(!menuState)}
                                aria-label={menuState == true ? 'Close Menu' : 'Open Menu'}
                                className="relative z-20 -m-2.5 -mr-4 block cursor-pointer p-2.5 lg:hidden">
                                <Menu className="group-data-[state=active]:rotate-180 group-data-[state=active]:scale-0 group-data-[state=active]:opacity-0 m-auto size-6 duration-200" />
                                <X className="group-data-[state=active]:rotate-0 group-data-[state=active]:scale-100 group-data-[state=active]:opacity-100 absolute inset-0 m-auto size-6 -rotate-180 scale-0 opacity-0 duration-200" />
                            </button>
                        </div>

                        <div className="absolute inset-0 m-auto hidden size-fit lg:block">
                            <ul className="flex gap-8 text-sm">
                                {menuItems.map((item, index) => (
                                    <li key={index}>
                                        <Link
                                            href={item.href}
                                            className="text-muted-foreground hover:text-foreground block duration-150 transition-colors">
                                            <span>{item.name}</span>
                                        </Link>
                                    </li>
                                ))}
                            </ul>
                        </div>

                        <div className="bg-background group-data-[state=active]:block lg:group-data-[state=active]:flex mb-6 hidden w-full flex-wrap items-center justify-end space-y-8 rounded-3xl border p-6 shadow-2xl shadow-zinc-300/20 md:flex-nowrap lg:m-0 lg:flex lg:w-fit lg:gap-6 lg:space-y-0 lg:border-transparent lg:bg-transparent lg:p-0 lg:shadow-none dark:shadow-none dark:lg:bg-transparent">
                            <div className="lg:hidden">
                                <ul className="space-y-6 text-base">
                                    {menuItems.map((item, index) => (
                                        <li key={index}>
                                            <Link
                                                href={item.href}
                                                className="text-muted-foreground hover:text-foreground block duration-150">
                                                <span>{item.name}</span>
                                            </Link>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                            <div className="flex w-full flex-col space-y-3 sm:flex-row sm:gap-3 sm:space-y-0 md:w-fit">
                                <Button
                                    asChild
                                    variant="outline"
                                    size="sm"
                                    className={cn(isScrolled && 'lg:hidden')}>
                                    <Link href="https://github.com/pozapas" target="_blank" rel="noopener noreferrer">
                                        <span>GitHub</span>
                                    </Link>
                                </Button>
                                <Button
                                    onClick={onStartResearch}
                                    size="sm"
                                    className={cn(isScrolled ? 'lg:inline-flex' : 'hidden', 'gradient-primary hover:opacity-90 text-white')}>
                                    <span>Start Research</span>
                                </Button>
                                <Button
                                    onClick={onStartResearch}
                                    size="sm"
                                    className={cn(!isScrolled ? 'lg:inline-flex' : 'hidden', 'gradient-primary hover:opacity-90 text-white')}>
                                    <Sparkles className="w-4 h-4 mr-1" />
                                    <span>Get Started</span>
                                </Button>
                            </div>
                        </div>
                    </div>
                </div>
            </nav>
        </header>
    )
}

const PaiperLogo = ({ className }: { className?: string }) => {
    return (
        <div className="flex items-center space-x-3">
            <div className="w-10 h-10 gradient-primary rounded-xl flex items-center justify-center shadow-modern">
                <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
                <span className={cn('text-2xl font-bold gradient-text', className)}>
                    pAIper
                </span>
                <div className="text-xs text-muted-foreground -mt-1 font-medium">
                    Research Simplified
                </div>
            </div>
        </div>
    )
}