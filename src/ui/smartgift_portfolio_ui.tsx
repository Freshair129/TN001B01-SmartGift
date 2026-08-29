import React, { useState, useEffect } from 'react';
import { 
  ChevronRight, 
  ChevronLeft, 
  CheckCircle2, 
  Users,
  Gift,
  Target,
  Calendar,
  Layers,
  Sparkles,
  ArrowRight,
  ArrowDown,
  Briefcase,
  Star,
  Coffee,
  Headphones,
  Leaf,
  Watch,
  Award,
  PackageSearch
} from 'lucide-react';

const InteractiveShiftSlide = () => {
  const [activeStep, setActiveStep] = useState(0);

  const steps = [
    { title: "ค้นหา Insight องค์กร", desc: "เจาะลึกโจทย์ว่าของขวัญจะถูกนำไปใช้ในบริบทไหน เพราะเราต้องรู้ว่า 'คนซื้อไม่ได้ใช้ คนใช้ไม่ได้ซื้อ' และผู้ที่มีอำนาจอนุมัติงบ อาจไม่ใช่คนที่มีอำนาจเลือกเสมอไป" },
    { title: "โฟกัสผู้รับปลายทาง", desc: "เปลี่ยนจุดชี้วัดความสำเร็จ (Surface) ไปที่ผู้รับของขวัญโดยตรง เพื่อให้เกิดการใช้งานจริง และสร้างประสบการณ์ที่เป็นภาพจำยอดเยี่ยมให้กับแบรนด์ของคุณ" },
    { title: "จัดสรรความพอดี", desc: "ออกแบบระดับการดูแลและติดตามผลให้พอเหมาะกับแต่ละกลุ่มเป้าหมาย โดยตั้งคำถามเสมอว่า 'เรากำลังจะแก้ปัญหาอะไรให้ลูกค้า' ไม่ใช่ 'เราจะขายอะไรดี'" },
    { title: "เสนอวิธีการแก้ปัญหา", desc: "ในฐานะผู้ออกแบบประสบการณ์ เราไม่ได้บังคับให้ลูกค้าต้องเลือกตามแคตตาล็อก แต่เรานำเสนอ 'ทางแก้ปัญหา' ที่ปรับแต่งมาเพื่อแคมเปญนั้นๆ โดยเฉพาะ" }
  ];

  return (
    <div className="flex flex-col h-full items-center justify-center w-full max-w-5xl mx-auto">
      <div className="text-center mb-16">
        <span className="text-[#86868B] font-mono text-xs tracking-[0.3em] uppercase mb-4 block">Process Design</span>
        <h3 className="text-4xl font-medium text-[#1D1D1F] tracking-tight">The Shift</h3>
      </div>

      {/* Old Way */}
      <div className="flex items-center gap-6 text-gray-400 mb-12 opacity-40">
         <span className="font-medium">เริ่มจากแคตตาล็อก</span>
         <ArrowRight className="w-4 h-4" />
         <span className="font-medium">เลือกสินค้า</span>
         <ArrowRight className="w-4 h-4" />
         <span className="font-medium">ขอราคา</span>
      </div>

      <div className="w-px h-16 bg-gradient-to-b from-gray-200 to-transparent mb-8"></div>

      {/* New Way - Interactive Stepper */}
      <div className="bg-white/50 backdrop-blur-xl p-3 rounded-2xl border border-gray-200/50 flex items-center gap-3 mb-12 shadow-sm">
        {steps.map((step, idx) => (
          <React.Fragment key={idx}>
            <button
              onClick={() => setActiveStep(idx)}
              className={`px-8 py-4 rounded-xl text-sm font-medium transition-all duration-500 outline-none ${
                activeStep === idx
                  ? 'bg-[#1D1D1F] text-white shadow-xl scale-105'
                  : 'bg-white text-[#86868B] border border-gray-100 hover:bg-gray-50'
              }`}
            >
              {step.title}
            </button>
            {idx < steps.length - 1 && <ArrowRight className="w-5 h-5 text-gray-300" />}
          </React.Fragment>
        ))}
      </div>

      {/* Details Card */}
      <div className="h-32 w-full max-w-2xl relative">
         {steps.map((step, idx) => (
            <div 
              key={idx}
              className={`absolute inset-0 bg-white p-8 rounded-[2rem] border border-gray-100 shadow-[0_20px_40px_rgba(0,0,0,0.04)] text-center transition-all duration-700 ease-[cubic-bezier(0.16,1,0.3,1)] ${
                activeStep === idx ? 'opacity-100 translate-y-0 z-10' : 'opacity-0 translate-y-4 pointer-events-none'
              }`}
            >
               <h4 className="text-xl font-semibold text-[#1D1D1F] mb-3">{step.title}</h4>
               <p className="text-[#86868B] font-light leading-relaxed">{step.desc}</p>
            </div>
         ))}
      </div>
    </div>
  );
};

const TargetMockupSlide = () => {
  const [activePack, setActivePack] = useState(0);
  const [showDetails, setShowDetails] = useState(false);

  const packs = [
    {
      id: "manager",
      title: "Manager Edition.",
      subtitle: "Team & Leadership",
      qty: "10 Sets",
      tier: "Select Tier",
      price: "Optimized for scale",
      desc: "ชุดของขวัญสำหรับผู้จัดการทีม เน้นฟังก์ชันการทำงานและการดูแลสุขภาพระหว่างวัน",
      icon: <Briefcase className="w-8 h-8 text-gray-900" strokeWidth={1.5} />,
      items: [
        { name: "Ergonomic Accessories", icon: <Watch className="w-6 h-6 text-gray-600" strokeWidth={1.5}/>, desc: "อุปกรณ์ซัพพอร์ตการทำงาน" },
        { name: "Specialty Coffee Blend", icon: <Coffee className="w-6 h-6 text-gray-600" strokeWidth={1.5}/>, desc: "เมล็ดกาแฟคั่วพิเศษ" },
        { name: "Digital Note Premium", icon: <Layers className="w-6 h-6 text-gray-600" strokeWidth={1.5}/>, desc: "สมุดจดอัจฉริยะ" }
      ],
      color: "bg-[#F5F5F7]"
    },
    {
      id: "partner",
      title: "Partner Premium.",
      subtitle: "Strategic Alliance",
      qty: "5 Sets",
      tier: "Signature Tier",
      price: "High-value impact",
      desc: "ชุดของขวัญสำหรับผู้บริหารและคู่ค้าคนสำคัญ เน้นภาพลักษณ์ ประสบการณ์ และความเอ็กซ์คลูซีฟสูงสุด",
      icon: <Award className="w-8 h-8 text-white" strokeWidth={1.5} />,
      items: [
        { name: "Executive Leather Folio", icon: <Briefcase className="w-6 h-6 text-gray-600" strokeWidth={1.5}/>, desc: "แฟ้มหนังแท้สลักชื่อ" },
        { name: "Fine Dining Experience", icon: <Star className="w-6 h-6 text-gray-600" strokeWidth={1.5}/>, desc: "เวาเชอร์ดินเนอร์มื้อพิเศษ" },
        { name: "Bespoke Wellness Set", icon: <Leaf className="w-6 h-6 text-gray-600" strokeWidth={1.5}/>, desc: "ชุดเครื่องหอมปรับสมดุล" }
      ],
      color: "bg-[#1D1D1F] text-white"
    }
  ];

  return (
    <div className="flex h-full items-center justify-center w-full max-w-6xl mx-auto gap-12">
      {/* Left: Selectors */}
      <div className="w-1/3 flex flex-col gap-4">
        <span className="text-[#86868B] font-mono text-xs tracking-[0.3em] uppercase mb-4">Targeting Mockup</span>
        <h3 className="text-4xl font-semibold text-[#1D1D1F] tracking-tight mb-8 leading-tight">
          กำหนดเป้าหมาย.<br/>แม่นยำและพอดี.
        </h3>
        
        <div className="space-y-4">
          {packs.map((pack, idx) => (
            <button
              key={pack.id}
              onClick={() => {
                setActivePack(idx);
                setShowDetails(false);
              }}
              className={`w-full text-left p-6 rounded-2xl transition-all duration-500 border ${
                activePack === idx 
                  ? 'bg-white border-gray-200 shadow-[0_20px_40px_rgba(0,0,0,0.04)] scale-105 z-10' 
                  : 'bg-transparent border-transparent hover:bg-gray-100 opacity-60'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-xl text-gray-900 tracking-tight">{pack.title}</span>
                {activePack === idx && <ChevronRight className="w-5 h-5 text-gray-400" />}
              </div>
              <div className="text-sm text-gray-500 font-medium">
                {pack.qty} • {pack.tier}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Right: Visual Display */}
      <div className="w-2/3 h-[520px] relative">
        {packs.map((pack, idx) => (
          <div 
            key={pack.id}
            className={`absolute inset-0 transition-all duration-700 ease-[cubic-bezier(0.16,1,0.3,1)] flex flex-col justify-center p-10 rounded-[2.5rem] border ${pack.id === 'manager' ? 'border-gray-100' : 'border-gray-800'} ${pack.color} shadow-inner overflow-hidden ${
              activePack === idx ? 'opacity-100 translate-x-0 pointer-events-auto' : 'opacity-0 translate-x-12 pointer-events-none'
            }`}
          >
            {/* Box Exterior View */}
            <div className={`transition-all duration-500 absolute inset-10 flex flex-col ${showDetails ? 'opacity-0 translate-y-8 pointer-events-none' : 'opacity-100 translate-y-0'}`}>
              <div className={`w-16 h-16 rounded-2xl flex items-center justify-center shadow-sm mb-8 ${pack.id === 'partner' ? 'bg-gray-800' : 'bg-white'}`}>
                {pack.icon}
              </div>
              
              <div className="flex gap-4 mb-6">
                <span className={`px-4 py-1.5 rounded-full text-xs font-semibold tracking-widest uppercase shadow-sm ${pack.id === 'partner' ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'}`}>
                  {pack.qty}
                </span>
                <span className={`px-4 py-1.5 rounded-full text-xs font-semibold tracking-widest uppercase shadow-sm ${pack.id === 'partner' ? 'bg-white text-gray-900' : 'bg-gray-900 text-white'}`}>
                  {pack.tier}
                </span>
              </div>

              <h4 className={`text-3xl font-semibold tracking-tight mb-4 ${pack.id === 'partner' ? 'text-white' : 'text-[#1D1D1F]'}`}>{pack.subtitle}</h4>
              <p className={`text-lg font-light leading-relaxed max-w-md mb-8 ${pack.id === 'partner' ? 'text-gray-400' : 'text-[#86868B]'}`}>
                {pack.desc}
              </p>

              <button 
                onClick={() => setShowDetails(true)}
                className={`mt-auto self-start flex items-center gap-2 px-6 py-3 rounded-full text-sm font-medium transition-transform hover:scale-105 ${pack.id === 'partner' ? 'bg-white text-black' : 'bg-[#1D1D1F] text-white'}`}
              >
                <PackageSearch className="w-4 h-4" />
                ดูรายละเอียดภายในเซ็ต
              </button>
            </div>

            {/* Unboxed / Details View */}
            <div className={`transition-all duration-500 absolute inset-10 flex flex-col ${showDetails ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-8 pointer-events-none'}`}>
              <div className="flex items-center justify-between mb-8">
                <h4 className={`text-2xl font-semibold tracking-tight ${pack.id === 'partner' ? 'text-white' : 'text-[#1D1D1F]'}`}>Inside the {pack.title}</h4>
                <button 
                  onClick={() => setShowDetails(false)}
                  className={`text-sm font-medium underline underline-offset-4 ${pack.id === 'partner' ? 'text-gray-400 hover:text-white' : 'text-[#86868B] hover:text-black'}`}
                >
                  ปิดกล่อง
                </button>
              </div>

              <div className="grid grid-cols-1 gap-4 h-full overflow-y-auto pr-2 pb-8">
                {pack.items.map((item, i) => (
                  <div key={i} className={`flex items-center p-4 rounded-2xl border ${pack.id === 'partner' ? 'bg-gray-800/50 border-gray-700' : 'bg-white border-gray-100 shadow-sm'}`}>
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center mr-4 ${pack.id === 'partner' ? 'bg-gray-700' : 'bg-gray-50'}`}>
                      {item.icon}
                    </div>
                    <div>
                      <div className={`font-semibold ${pack.id === 'partner' ? 'text-white' : 'text-gray-900'}`}>{item.name}</div>
                      <div className={`text-sm font-light mt-1 ${pack.id === 'partner' ? 'text-gray-400' : 'text-gray-500'}`}>{item.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
          </div>
        ))}
      </div>
    </div>
  );
};

const ProductSetMockupSlide = () => {
  return (
    <div className="flex flex-col h-full items-center justify-center w-full">
      <div className="text-center mb-12">
        <span className="text-[#86868B] font-mono text-xs tracking-[0.3em] uppercase mb-4 block">Product Design Mockup</span>
        <h2 className="text-5xl font-semibold text-[#1D1D1F] tracking-tight">Set A.</h2>
        <p className="text-xl text-[#86868B] font-light mt-4">
          Tech <span className="mx-2 text-gray-300">×</span> Wellness <span className="mx-2 text-gray-300">×</span> Lifestyle
        </p>
      </div>

      <div className="w-full max-w-5xl aspect-[2/1] grid grid-cols-3 grid-rows-2 gap-6 relative">
        
        {/* Core Product: Tech */}
        <div className="col-span-2 row-span-2 bg-white rounded-[2rem] border border-gray-100 shadow-[0_20px_40px_rgba(0,0,0,0.03)] p-10 flex flex-col justify-between group hover:shadow-[0_30px_60px_rgba(0,0,0,0.06)] transition-all duration-500">
          <div className="flex justify-between items-start z-10">
            <div>
              <span className="text-[10px] font-mono text-gray-400 tracking-widest uppercase block mb-2">Primary Item • Tech</span>
              <h3 className="text-2xl font-semibold text-gray-900">Spatial Audio Hub</h3>
            </div>
            <Headphones className="w-6 h-6 text-gray-400" strokeWidth={1.5} />
          </div>
          
          {/* Wireframe Graphic Representation */}
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
             <div className="w-56 h-56 rounded-full border border-gray-100 bg-gray-50/50 flex items-center justify-center group-hover:scale-105 transition-transform duration-700">
                <div className="w-40 h-40 rounded-full bg-white shadow-xl flex items-center justify-center">
                   <Headphones className="w-16 h-16 text-[#1D1D1F]" strokeWidth={1} />
                </div>
             </div>
          </div>
        </div>

        {/* Secondary Product: Lifestyle */}
        <div className="col-span-1 row-span-1 bg-white rounded-[2rem] border border-gray-100 shadow-sm p-8 flex flex-col justify-between group hover:shadow-md transition-all duration-500 relative overflow-hidden">
          <div className="flex justify-between items-start z-10">
            <div>
              <span className="text-[10px] font-mono text-gray-400 tracking-widest uppercase block mb-1">Addition • Lifestyle</span>
              <h3 className="text-lg font-medium text-gray-900">Titanium Tumbler</h3>
            </div>
          </div>
           {/* Wireframe Graphic Representation */}
           <div className="absolute bottom-[-10px] right-6 w-20 h-28 bg-gradient-to-t from-gray-100 to-white rounded-t-xl border border-gray-200 flex items-center justify-center group-hover:-translate-y-2 transition-transform duration-500">
              <Coffee className="w-8 h-8 text-gray-300" strokeWidth={1.5} />
           </div>
        </div>

        {/* Tertiary Product: Wellness */}
        <div className="col-span-1 row-span-1 bg-[#F5F5F7] rounded-[2rem] border border-gray-100 shadow-inner p-8 flex flex-col justify-between group hover:shadow-md transition-all duration-500 relative overflow-hidden">
          <div className="flex justify-between items-start z-10">
            <div>
              <span className="text-[10px] font-mono text-gray-400 tracking-widest uppercase block mb-1">Addition • Wellness</span>
              <h3 className="text-lg font-medium text-gray-900">Focus Blend Oil</h3>
            </div>
          </div>
          {/* Wireframe Graphic Representation */}
          <div className="absolute bottom-4 right-8 w-12 h-16 bg-white rounded-lg shadow-sm border border-gray-100 flex items-center justify-center group-hover:-translate-y-2 transition-transform duration-500">
            <Leaf className="w-6 h-6 text-gray-400" strokeWidth={1.5} />
          </div>
        </div>

      </div>
    </div>
  );
};

const InteractiveGiftStackSlide = () => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div className="flex h-full items-center justify-center relative w-full">
      <style>{`
        .preserve-3d { transform-style: preserve-3d; }
        .iso-container { transform: rotateX(60deg) rotateZ(-45deg); transition: transform 0.8s cubic-bezier(0.16, 1, 0.3, 1); }
        .iso-layer { transition: all 1s cubic-bezier(0.16, 1, 0.3, 1); }
        .counter-iso { transform: rotateZ(45deg) rotateX(-60deg); }
      `}</style>

      <div className="w-1/3 pr-12 space-y-6">
        <h3 className="text-4xl font-semibold text-[#1D1D1F] tracking-tight">The Gift Stack.</h3>
        <p className="text-xl text-[#86868B] font-light leading-relaxed">
          เปลี่ยนตารางที่ซับซ้อน เป็นเลเยอร์แห่งการออกแบบ. 
          <br/><br/>
          ชี้ที่รูปภาพด้านขวาเพื่อดูโครงสร้างแต่ละชั้น.
        </p>
      </div>

      <div className="w-2/3 h-full flex justify-center items-center perspective-[2000px]">
        <div 
          className="relative w-[400px] h-[400px] preserve-3d iso-container cursor-pointer"
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
        >
          
          {/* Ambient Shadow */}
          <div className={`absolute inset-0 bg-gray-200 blur-[60px] transform translate-z-[-50px] rounded-full transition-opacity duration-700 ${isHovered ? 'opacity-100' : 'opacity-50'}`}></div>

          {/* Layer 1: Base */}
          <div 
            className="absolute inset-0 bg-white border border-gray-100 rounded-3xl flex items-end p-6 preserve-3d iso-layer" 
            style={{ 
              transform: `translateZ(${isHovered ? '10px' : '0px'})`,
              boxShadow: isHovered ? '0 15px 35px rgba(0,0,0,0.05)' : 'inset 0 0 20px rgba(0,0,0,0.02)'
            }}
          >
            <div className="counter-iso text-gray-400 font-mono text-[10px] tracking-widest uppercase">Foundation</div>
          </div>

          {/* Layer 2: Segment */}
          <div 
            className="absolute inset-4 bg-gray-50/80 backdrop-blur-md border border-gray-200/50 rounded-[1.5rem] flex items-center justify-center preserve-3d iso-layer" 
            style={{ 
              transform: `translateZ(${isHovered ? '70px' : '20px'})`,
              boxShadow: isHovered ? '0 20px 40px rgba(0,0,0,0.05)' : 'none'
            }}
          >
            <div className="counter-iso flex flex-col items-center">
              <span className="text-gray-500 font-medium tracking-widest text-xs uppercase">VIP Member</span>
            </div>
          </div>

          {/* Layer 3: Tier */}
          <div 
            className="absolute inset-8 bg-white/70 backdrop-blur-2xl border border-white rounded-[1.2rem] flex items-center justify-center preserve-3d iso-layer overflow-hidden" 
            style={{ 
              transform: `translateZ(${isHovered ? '140px' : '40px'})`,
              boxShadow: isHovered ? '0 30px 60px rgba(0,0,0,0.08)' : '0 8px 30px rgba(0,0,0,0.04)'
            }}
          >
            <div className="absolute inset-0 bg-[linear-gradient(135deg,rgba(255,255,255,0.8)_0%,transparent_100%)]"></div>
            <div className="counter-iso">
              <h4 className="text-3xl font-semibold text-gray-900 tracking-tight">Signature</h4>
            </div>
          </div>

          {/* Layer 4: Theme (Items) */}
          <div 
            className="absolute inset-16 bg-gray-100/50 backdrop-blur-md border border-white/50 rounded-xl grid grid-cols-2 gap-3 p-3 preserve-3d iso-layer" 
            style={{ transform: `translateZ(${isHovered ? '220px' : '60px'})` }}
          >
            <div className="bg-white/80 border border-white rounded-lg flex flex-col items-center justify-center shadow-sm">
              <div className="counter-iso flex flex-col items-center"><Target className="w-4 h-4 text-gray-400 mb-1" strokeWidth={1.5}/><span className="text-[9px] text-gray-500 font-mono">Care</span></div>
            </div>
            <div className="bg-white/80 border border-white rounded-lg flex flex-col items-center justify-center shadow-sm">
              <div className="counter-iso flex flex-col items-center"><Layers className="w-4 h-4 text-gray-400 mb-1" strokeWidth={1.5}/><span className="text-[9px] text-gray-500 font-mono">Taste</span></div>
            </div>
          </div>

          {/* Layer 5: Format (Card) */}
          <div 
            className="absolute inset-x-24 inset-y-16 bg-white/90 backdrop-blur-3xl border border-white rounded-xl flex items-center justify-center preserve-3d iso-layer" 
            style={{ 
              transform: `translateZ(${isHovered ? '300px' : '80px'})`,
              boxShadow: isHovered ? '0 40px 80px rgba(0,0,0,0.1)' : '0 10px 30px rgba(0,0,0,0.06)'
            }}
          >
            <div className="absolute top-0 left-0 w-full h-full bg-[linear-gradient(to_bottom_right,rgba(255,255,255,1),transparent)] rounded-xl pointer-events-none"></div>
            <div className="counter-iso flex flex-col items-center">
              <Sparkles className="text-gray-900 w-4 h-4 mb-2" strokeWidth={1.5}/>
              <span className="text-gray-600 font-medium text-[10px] tracking-wider uppercase">Hybrid</span>
            </div>
          </div>
          
        </div>
      </div>
    </div>
  );
};

const slideDeck = [
  // Slide 1: Title
  {
    id: 1,
    content: (
      <div className="flex flex-col items-center justify-center h-full text-center space-y-6">
        <span className="text-[#86868B] font-mono text-xs tracking-[0.3em] uppercase">Confidential Proposal</span>
        <h1 className="text-6xl md:text-7xl font-semibold text-[#1D1D1F] tracking-tight">
          SmartGift 2026.
        </h1>
        <p className="text-2xl text-[#86868B] font-light max-w-2xl mx-auto">
          Brand & Product Portfolio Architecture.
        </p>
      </div>
    )
  },
  
  // Slide 2: The Pivot Statement
  {
    id: 2,
    content: (
      <div className="flex flex-col items-center justify-center h-full text-center">
        <h2 className="text-4xl md:text-5xl font-medium text-[#1D1D1F] leading-snug tracking-tight max-w-4xl">
          ถึงเวลาเปลี่ยนจาก<br/>
          การเป็น <span className="text-transparent bg-clip-text bg-gradient-to-r from-gray-500 to-gray-900">“ผู้จัดหาสินค้า”</span><br/>
          สู่การเป็น <span className="text-transparent bg-clip-text bg-gradient-to-r from-gray-500 to-gray-900">“ผู้ออกแบบประสบการณ์”</span>
        </h2>
      </div>
    )
  },

  // Slide 3: The Pain (Numbers)
  {
    id: 3,
    content: (
      <div className="flex flex-col h-full justify-center">
        <div className="text-center mb-16">
          <h3 className="text-2xl text-[#86868B] font-medium tracking-tight">The Current Reality</h3>
        </div>
        <div className="grid grid-cols-2 gap-12 w-full max-w-4xl mx-auto">
          <div className="flex flex-col items-center justify-center p-12 bg-white rounded-3xl shadow-[0_20px_40px_rgba(0,0,0,0.03)] border border-gray-100">
            <span className="text-7xl font-semibold text-[#1D1D1F] mb-4 tracking-tighter">703</span>
            <span className="text-[#86868B] font-medium tracking-wide">Gift Sets</span>
          </div>
          <div className="flex flex-col items-center justify-center p-12 bg-white rounded-3xl shadow-[0_20px_40px_rgba(0,0,0,0.03)] border border-gray-100">
            <span className="text-7xl font-semibold text-[#1D1D1F] mb-4 tracking-tighter">2,055</span>
            <span className="text-[#86868B] font-medium tracking-wide">Catalog SKUs</span>
          </div>
        </div>
        <div className="text-center mt-12">
          <p className="text-xl text-[#1D1D1F] font-medium">ลูกค้าจมอยู่กับตัวเลือก. เราสูญเสียความชัดเจน.</p>
        </div>
      </div>
    )
  },

  // Slide 4: The Core Insight (NEW)
  {
    id: 4,
    content: (
      <div className="flex flex-col items-center justify-center h-full text-center space-y-10 w-full max-w-5xl mx-auto">
        <span className="text-[#86868B] font-mono text-xs tracking-[0.3em] uppercase block">The Core Insight</span>

        <div className="space-y-6">
           <h2 className="text-5xl md:text-6xl font-semibold text-[#1D1D1F] tracking-tight">
             คนซื้อไม่ได้ใช้ <span className="text-gray-300 mx-3 font-light">|</span> <span className="text-gray-400">คนใช้ไม่ได้ซื้อ</span>
           </h2>
           
           <h2 className="text-4xl md:text-5xl font-semibold text-[#1D1D1F] tracking-tight">
             อำนาจตัดสินใจซื้อ <span className="text-gray-300 font-light mx-3">≠</span> อำนาจตัดสินใจเลือก
           </h2>
        </div>

        <div className="w-12 h-px bg-gray-300 mx-auto mt-4 mb-4"></div>

        <p className="text-xl text-[#86868B] font-light max-w-3xl mx-auto leading-relaxed">
          แผนกจัดซื้ออาจเป็นผู้อนุมัติงบ แต่ถ้าผู้บริหารบอกว่า "ไม่เอา" ทุกอย่างคือจบ.<br/><br/>
          เราจึงไม่ออกแบบเพียงเพื่อเอาใจคนซื้อ แต่เราโฟกัสไปที่ <strong className="text-gray-900 font-medium">"ผู้รับ"</strong> <br/>
          เพื่อให้ของขวัญสร้างประสบการณ์ที่ดีที่สุด และกลายเป็นภาพจำที่ยอดเยี่ยมของแบรนด์
        </p>
      </div>
    )
  },

  // Slide 5: The Framework Shift (Previously Slide 4)
  {
    id: 5,
    content: <InteractiveShiftSlide />
  },

  // Slide 6: The Advantage (Replaced with Executive Insight)
  {
    id: 6,
    content: (
      <div className="flex flex-col items-center justify-center h-full w-full max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <span className="text-[#86868B] font-mono text-xs tracking-[0.3em] uppercase mb-4 block">The SmartGift Advantage</span>
          <h2 className="text-4xl md:text-5xl font-semibold text-[#1D1D1F] tracking-tight leading-tight">
            พลิกจุดอ่อนเรื่อง "ขั้นต่ำ" (MOQ)<br/>ให้เป็น "มูลค่า" ที่สูงขึ้น
          </h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
          {/* Old Mindset */}
          <div className="p-10 bg-white rounded-[2rem] border border-gray-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)] flex flex-col justify-center">
            <span className="text-[#86868B] font-mono text-xs tracking-widest uppercase mb-4">The MOQ Dilemma</span>
            <h4 className="text-2xl font-medium text-[#1D1D1F] mb-4">พยายามขายให้ได้ "จำนวน" เยอะๆ</h4>
            <p className="text-[#86868B] leading-relaxed font-light">
              จุดอ่อนของธุรกิจพรีเมียมคือการบังคับยอดสั่งซื้อขั้นต่ำ ลูกค้ามักไม่อยากจ่ายเพิ่มเพื่อซื้อแจกคนที่ไม่จำเป็นต้องให้ ทำให้เสียโอกาสปิดการขายและกลายเป็นการต่อรองราคา
            </p>
          </div>
          {/* New Mindset / Insight */}
          <div className="p-10 bg-[#1D1D1F] rounded-[2rem] shadow-2xl flex flex-col justify-center relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-gray-700 to-transparent opacity-20 rounded-full blur-3xl -translate-y-1/2 translate-x-1/4"></div>
            <span className="text-gray-400 font-mono text-xs tracking-widest uppercase mb-4">The Executive Insight</span>
            <h4 className="text-2xl font-medium text-white mb-4">เพิ่มยอดขายด้วย "การยกระดับ" (Tiering)</h4>
            <p className="text-gray-400 leading-relaxed font-light">
              ผู้บริหารคือกลุ่มเป้าหมายที่มีจำนวนน้อย แต่ <span className="text-white font-medium">"จำเป็นต้องให้ และต้องให้ของดี"</span> โมเดลพอร์ตฟอลิโอนี้ทำให้ลูกค้ายินดีจ่ายงบสูงขึ้นสำหรับเซ็ต Signature (เช่น 5-10 ชิ้น) โดยไม่ต้องแบกภาระสต็อกส่วนเกิน
            </p>
          </div>
        </div>
      </div>
    )
  },

  // Slide 7: The Architecture (Light 3D)
  {
    id: 7,
    content: <InteractiveGiftStackSlide />
  },

  // Slide 8: Tier 1
  {
    id: 8,
    content: (
      <div className="flex flex-col h-full items-center justify-center text-center">
        <span className="text-[#86868B] font-mono text-sm tracking-widest uppercase mb-4">Base Model</span>
        <h2 className="text-7xl font-semibold text-[#1D1D1F] tracking-tight mb-8">Reach.</h2>
        <p className="text-xl text-[#86868B] font-light max-w-xl leading-relaxed">
          เน้นการเข้าถึงคนจำนวนมาก สร้าง Brand Recall.<br/>
          เหมาะกับ Mass Event และผู้ร่วมงานทั่วไป.
        </p>
      </div>
    )
  },

  // Slide 9: Tier 2
  {
    id: 9,
    content: (
      <div className="flex flex-col h-full items-center justify-center text-center">
        <span className="text-[#86868B] font-mono text-sm tracking-widest uppercase mb-4">Plus Model</span>
        <h2 className="text-7xl font-semibold text-[#1D1D1F] tracking-tight mb-8">Select.</h2>
        <p className="text-xl text-[#86868B] font-light max-w-xl leading-relaxed">
          คัดสรร Theme ให้เหมาะกับกลุ่มเฉพาะ.<br/>
          สำหรับพนักงาน, สมาชิก และสื่อทั่วไป.
        </p>
      </div>
    )
  },

  // Slide 10: Tier 3
  {
    id: 10,
    content: (
      <div className="flex flex-col h-full items-center justify-center text-center">
        <span className="text-[#86868B] font-mono text-sm tracking-widest uppercase mb-4">Pro Model</span>
        <h2 className="text-7xl font-semibold text-[#1D1D1F] tracking-tight mb-8">Signature.</h2>
        <p className="text-xl text-[#86868B] font-light max-w-xl leading-relaxed">
          ดูแล VIP อย่างตั้งใจ ภาพลักษณ์สูงสุด.<br/>
          สำหรับ Key Media และ VIP Member.
        </p>
      </div>
    )
  },

  // Slide 11: Tier 4
  {
    id: 11,
    content: (
      <div className="flex flex-col h-full items-center justify-center text-center">
        <span className="text-[#86868B] font-mono text-sm tracking-widest uppercase mb-4">Pro Max Model</span>
        <h2 className="text-7xl font-semibold text-[#1D1D1F] tracking-tight mb-8">Bespoke.</h2>
        <p className="text-xl text-[#86868B] font-light max-w-xl leading-relaxed">
          งานคราฟต์ที่ออกแบบใหม่เฉพาะแคมเปญ.<br/>
          สำหรับ Board Member และบุคคลสำคัญสูงสุด.
        </p>
      </div>
    )
  },

  // Slide 12: Target Mockup (Manager 10 vs Partner 5)
  {
    id: 12,
    content: <TargetMockupSlide />
  },

  // Slide 13: Product Set Mockup (Set A: Life + Wellness + Tech)
  {
    id: 13,
    content: <ProductSetMockupSlide />
  },

  // Slide 14: Action
  {
    id: 14,
    content: (
      <div className="flex flex-col h-full items-center justify-center">
        <h2 className="text-4xl font-semibold text-[#1D1D1F] tracking-tight mb-16 text-center">
          The 90-Day Pilot.
        </h2>
        
        <div className="grid grid-cols-2 gap-8 w-full max-w-4xl">
          <div className="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm">
            <h4 className="text-lg font-medium text-gray-900 mb-6 border-b border-gray-100 pb-4">3 Targets</h4>
            <ul className="space-y-4 text-[#86868B]">
              <li className="flex items-center gap-3"><CheckCircle2 className="w-5 h-5 text-gray-900" strokeWidth={1.5}/> Customer Appreciation</li>
              <li className="flex items-center gap-3"><CheckCircle2 className="w-5 h-5 text-gray-900" strokeWidth={1.5}/> Launch Event & PR</li>
              <li className="flex items-center gap-3"><CheckCircle2 className="w-5 h-5 text-gray-900" strokeWidth={1.5}/> Employee Recognition</li>
            </ul>
          </div>

          <div className="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm">
            <h4 className="text-lg font-medium text-gray-900 mb-6 border-b border-gray-100 pb-4">Decisions Required</h4>
            <ul className="space-y-4 text-[#86868B]">
              <li className="flex items-center gap-3"><span className="w-5 h-5 rounded-full border border-gray-300"></span> Approve Positioning</li>
              <li className="flex items-center gap-3"><span className="w-5 h-5 rounded-full border border-gray-300"></span> Approve Tiers</li>
              <li className="flex items-center gap-3"><span className="w-5 h-5 rounded-full border border-gray-300"></span> Appoint Pilot Task Force</li>
            </ul>
          </div>
        </div>
      </div>
    )
  }
];

export default function SmartGiftPortfolio() {
  const [currentSlide, setCurrentSlide] = useState(0);

  const nextSlide = () => setCurrentSlide(prev => Math.min(prev + 1, slideDeck.length - 1));
  const prevSlide = () => setCurrentSlide(prev => Math.max(prev - 1, 0));

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'ArrowRight') nextSlide();
      if (e.key === 'ArrowLeft') prevSlide();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <>
      {/* ฝังฟอนต์ Prompt (ไม่มีหัว) เข้าไปในโปรเจกต์ */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600&display=swap');
        h1, h2, h3, h4, h5, h6, p, span, button, div {
          font-family: 'Prompt', sans-serif !important;
        }
      `}</style>
      
      <div className="min-h-screen bg-[#F5F5F7] flex flex-col font-sans selection:bg-gray-200 selection:text-black">
        
        {/* Top Header */}
        <header className="absolute top-0 w-full z-50">
        </header>

      {/* Main Content Area */}
      <main className="flex-grow flex items-center justify-center p-8 relative overflow-hidden">
        
        {/* Subtle Background Glows (White mode) */}
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-white blur-[100px] rounded-full pointer-events-none"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-gray-100 blur-[100px] rounded-full pointer-events-none"></div>

        {/* Slide Container - Borderless, clean */}
        <div className="w-full max-w-[1200px] h-[700px] relative z-10 flex flex-col">
          
          {/* Active Slide Content */}
          <div className="flex-grow relative">
            <div className="absolute inset-0 transition-opacity duration-500">
              {slideDeck[currentSlide].content}
            </div>
          </div>

        </div>
      </main>

      {/* Footer Navigation (Apple-style dots) */}
      <footer className="absolute bottom-10 w-full z-50">
        <div className="flex flex-col items-center gap-6">
          
          <div className="flex items-center gap-8">
            <button 
              onClick={prevSlide}
              disabled={currentSlide === 0}
              className="text-[#86868B] hover:text-[#1D1D1F] disabled:opacity-20 transition-colors"
            >
              <ChevronLeft className="w-6 h-6" strokeWidth={1.5} />
            </button>
            
            <div className="flex gap-2.5">
              {slideDeck.map((_, idx) => (
                <button 
                  key={idx}
                  onClick={() => setCurrentSlide(idx)}
                  className={`rounded-full transition-all duration-500 ease-in-out ${
                    currentSlide === idx 
                      ? 'bg-[#1D1D1F] w-8 h-1.5' 
                      : 'bg-gray-300 w-1.5 h-1.5 hover:bg-gray-400'
                  }`}
                />
              ))}
            </div>

            <button 
              onClick={nextSlide}
              disabled={currentSlide === slideDeck.length - 1}
              className="text-[#86868B] hover:text-[#1D1D1F] disabled:opacity-20 transition-colors"
            >
              <ChevronRight className="w-6 h-6" strokeWidth={1.5} />
            </button>
          </div>
          
          <div className="text-[10px] font-mono text-gray-400 tracking-[0.2em] uppercase">
            {String(currentSlide + 1).padStart(2, '0')} / {String(slideDeck.length).padStart(2, '0')}
          </div>

        </div>
      </footer>

    </div>
    </>
  );
}