import React from 'react'
import { Github, Linkedin, Mail, ExternalLink, Award, Users, BookOpen, Code } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { AnimatedGroup } from '@/components/ui/animated-group'

export function AboutSection() {
    return (
        <section id="about" className="bg-gradient-to-br from-background via-muted/20 to-background py-20 md:py-32">
            <div className="max-w-6xl mx-auto px-6">
                <AnimatedGroup preset="slide">
                    <div className="text-center mb-16">
                        <div className="inline-block p-4 rounded-2xl bg-primary/10 mb-6">
                            <Award className="w-8 h-8 text-primary mx-auto" />
                        </div>
                        <h2 className="text-3xl md:text-4xl font-bold mb-6 gradient-text">
                            Open Source Research Tool
                        </h2>
                        <p className="text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
                            pAIper is an open-source project created by Amir Rafe to help researchers and students 
                            find relevant academic papers more efficiently.
                        </p>
                    </div>
                </AnimatedGroup>

                <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
                    {/* Creator Profile */}
                    <AnimatedGroup preset="blur-slide">
                        <div className="glass rounded-3xl p-8 shadow-modern-xl">
                            <div className="flex items-start gap-6 mb-8">
                                <div className="w-20 h-20 gradient-primary rounded-2xl flex items-center justify-center text-white font-bold text-2xl shrink-0">
                                    AR
                                </div>
                                <div>
                                    <h3 className="text-2xl font-bold text-foreground mb-2">Amir Rafe</h3>
                                    <p className="text-primary font-semibold mb-3">Postdoctoral Researcher</p>
                                    <p className="text-muted-foreground leading-relaxed">
                                        AI in Transportation (AIT) Lab • Texas State University
                                    </p>
                                </div>
                            </div>

                            <div className="space-y-4 mb-8">
                                <div className="flex items-center gap-3">
                                    <BookOpen className="w-5 h-5 text-primary" />
                                    <span className="text-foreground">Ph.D. Civil & Environmental Engineering</span>
                                </div>
                                <div className="flex items-center gap-3">
                                    <Code className="w-5 h-5 text-primary" />
                                    <span className="text-foreground">15+ Years in Transportation Engineering</span>
                                </div>
                                <div className="flex items-center gap-3">
                                    <Award className="w-5 h-5 text-primary" />
                                    <span className="text-foreground">Expert in Causal AI & Safety Systems</span>
                                </div>
                            </div>

                            <div className="flex gap-4">
                                <Button asChild variant="outline" size="sm" className="flex-1">
                                    <a href="https://pozapas.github.io" target="_blank" rel="noopener noreferrer">
                                        <ExternalLink className="w-4 h-4 mr-2" />
                                        View Portfolio
                                    </a>
                                </Button>
                                <Button asChild variant="outline" size="sm">
                                    <a href="https://linkedin.com/in/amir-rafe-08770854" target="_blank" rel="noopener noreferrer">
                                        <Linkedin className="w-4 h-4" />
                                    </a>
                                </Button>
                                <Button asChild variant="outline" size="sm">
                                    <a href="https://github.com/pozapas" target="_blank" rel="noopener noreferrer">
                                        <Github className="w-4 h-4" />
                                    </a>
                                </Button>
                            </div>
                        </div>
                    </AnimatedGroup>

                    {/* Mission & Vision */}
                    <AnimatedGroup preset="scale">
                        <div className="space-y-8">
                            <div>
                                <h3 className="text-2xl font-bold text-foreground mb-4 flex items-center gap-3">
                                    <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-emerald-600 rounded-lg flex items-center justify-center">
                                        <Users className="w-5 h-5 text-white" />
                                    </div>
                                    About This Project
                                </h3>
                                <p className="text-muted-foreground text-lg leading-relaxed">
                                    An open-source tool designed to help researchers, students, and academics discover 
                                    relevant papers more efficiently using AI-powered search and analysis.
                                </p>
                            </div>

                            <div>
                                <h3 className="text-2xl font-bold text-foreground mb-4 flex items-center gap-3">
                                    <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-lg flex items-center justify-center">
                                        <BookOpen className="w-5 h-5 text-white" />
                                    </div>
                                    Why pAIper?
                                </h3>
                                <div className="space-y-3 text-muted-foreground">
                                    <p className="flex items-start gap-3">
                                        <span className="w-2 h-2 bg-primary rounded-full mt-2 shrink-0"></span>
                                        <span>Created by a researcher who understands the research process</span>
                                    </p>
                                    <p className="flex items-start gap-3">
                                        <span className="w-2 h-2 bg-primary rounded-full mt-2 shrink-0"></span>
                                        <span>Combines AI technology with academic methodology</span>
                                    </p>
                                    <p className="flex items-start gap-3">
                                        <span className="w-2 h-2 bg-primary rounded-full mt-2 shrink-0"></span>
                                        <span>Free and open-source for the research community</span>
                                    </p>
                                    <p className="flex items-start gap-3">
                                        <span className="w-2 h-2 bg-primary rounded-full mt-2 shrink-0"></span>
                                        <span>Continuously improved based on user feedback</span>
                                    </p>
                                </div>
                            </div>

                            <div className="pt-6">
                                <div className="glass rounded-2xl p-6">
                                    <h4 className="font-bold text-foreground mb-3">Research Background</h4>
                                    <div className="grid grid-cols-2 gap-4 text-sm">
                                        <div className="text-center">
                                            <div className="text-2xl font-bold text-primary">15+</div>
                                            <div className="text-muted-foreground">Years Experience</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-2xl font-bold text-primary">OSS</div>
                                            <div className="text-muted-foreground">Open Source</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </AnimatedGroup>
                </div>

                {/* Contact CTA */}
                <AnimatedGroup preset="slide" className="text-center mt-16">
                    <div className="glass rounded-3xl p-8 max-w-2xl mx-auto">
                        <h3 className="text-2xl font-bold text-foreground mb-4">Questions or Feedback?</h3>
                        <p className="text-muted-foreground mb-6 leading-relaxed">
                            Found a bug, have a suggestion, or want to contribute? Feel free to reach out or 
                            contribute to the project on GitHub.
                        </p>
                        <div className="flex gap-4 justify-center">
                            <Button asChild size="lg" className="gradient-primary text-white hover:opacity-90">
                                <a href="mailto:amir.rafe@txstate.edu">
                                    <Mail className="w-5 h-5 mr-2" />
                                    Contact Amir
                                </a>
                            </Button>
                            <Button asChild variant="outline" size="lg">
                                <a href="https://github.com/pozapas" target="_blank" rel="noopener noreferrer">
                                    <Github className="w-5 h-5 mr-2" />
                                    GitHub
                                </a>
                            </Button>
                        </div>
                    </div>
                </AnimatedGroup>
            </div>
        </section>
    )
}