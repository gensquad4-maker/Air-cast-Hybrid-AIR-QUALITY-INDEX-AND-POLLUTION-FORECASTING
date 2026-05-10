import { motion } from 'framer-motion';
import { Activity, Wind, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import MagneticButton from '../ui/MagneticButton';

const HeroSection = () => {
  const scrollToAbout = () => {
    document.getElementById('about')?.scrollIntoView({ behavior: 'smooth' });
  };

  const textVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.8, ease: [0.22, 1, 0.36, 1] as const }
    }
  };

  return (
    <section id="home" className="relative min-h-screen flex items-center justify-center overflow-hidden bg-slate-50 perspective-1000">
      {/* Cinematic Background - Sky Light */}
      <div className="absolute inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-b from-sky-50 via-white to-white" />

        {/* Animated Sky Blobs */}
        <motion.div
          animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.5, 0.3], rotate: [0, 10, 0] }}
          transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
          className="absolute top-[-20%] left-[-10%] w-[60vw] h-[60vw] rounded-full bg-sky-200/40 blur-[100px]"
        />
        <motion.div
          animate={{ scale: [1, 1.1, 1], opacity: [0.2, 0.4, 0.2], rotate: [0, -15, 0] }}
          transition={{ duration: 20, repeat: Infinity, ease: "linear", delay: 2 }}
          className="absolute bottom-[-10%] right-[-10%] w-[50vw] h-[50vw] rounded-full bg-blue-200/30 blur-[100px]"
        />
      </div>

      <div className="section-container relative z-10 text-center">
        <motion.div
          initial="hidden"
          animate="visible"
          variants={textVariants}
          className="mb-8"
        >
          <span className="px-6 py-2 rounded-full glass-panel text-xs font-bold uppercase tracking-[0.3em] text-sky-600 border border-sky-100 shadow-sm">
            FINAL YEAR PROJECT &bull; B.TECH AI & DS
          </span>
        </motion.div>

        <motion.h1
          initial="hidden"
          animate="visible"
          variants={{
            hidden: { opacity: 0 },
            visible: { opacity: 1, transition: { staggerChildren: 0.2 } }
          }}
          className="font-serif text-6xl md:text-9xl font-black text-slate-900 mb-8 tracking-tighter leading-[0.9]"
        >
          <motion.span variants={textVariants} className="block text-slate-800 drop-shadow-sm">AI-POWERED</motion.span>
          <motion.span variants={textVariants} className="block text-gradient-animate">SKYPLUS</motion.span>
        </motion.h1>

        <motion.p
          initial="hidden"
          animate="visible"
          variants={textVariants}
          transition={{ delay: 0.4 }}
          className="text-slate-600 max-w-2xl mx-auto text-xl md:text-2xl font-light mb-12 leading-relaxed"
        >
          Precision pollution analytics using advanced <span className="text-sky-600 font-medium">Hybrid CNN-LSTM</span> Neural Networks.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.8 }}
          className="flex flex-wrap justify-center gap-6"
        >
          <MagneticButton onClick={scrollToAbout}>
            <button className="btn-shine-light px-10 py-5 rounded-2xl bg-white border border-slate-200 text-slate-900 font-black uppercase tracking-widest hover:bg-slate-50 transition-all shadow-lg hover:shadow-xl">
              Explore Data
            </button>
          </MagneticButton>

          <Link to="/predictor">
            <MagneticButton>
              <div className="btn-shine-light px-10 py-5 rounded-2xl bg-sky-500 text-white font-black uppercase tracking-widest hover:scale-105 transition-all shadow-lg shadow-sky-200 flex items-center gap-3">
                Launch Predictor
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </div>
            </MagneticButton>
          </Link>
        </motion.div>
      </div>

      {/* Floating 3D Elements */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <motion.div
          animate={{ y: [0, -30, 0], rotate: [0, 5, 0], opacity: [0.6, 0.8, 0.6] }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-[20%] left-[10%] text-sky-200/80"
        >
          <Wind size={120} />
        </motion.div>
        <motion.div
          animate={{ y: [0, 40, 0], rotate: [0, -10, 0], opacity: [0.6, 0.8, 0.6] }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut", delay: 1 }}
          className="absolute bottom-[20%] right-[10%] text-blue-200/80"
        >
          <Activity size={120} />
        </motion.div>
      </div>
    </section>
  );
};

export default HeroSection;
