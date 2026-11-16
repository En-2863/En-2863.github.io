// get the ninja-keys element
const ninja = document.querySelector('ninja-keys');

// add the home and posts menu items
ninja.data = [{
    id: "nav-about",
    title: "About",
    section: "Navigation",
    handler: () => {
      window.location.href = "/";
    },
  },{id: "nav-blog",
          title: "blog",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/blog/";
          },
        },{id: "nav-publications",
          title: "publications",
          description: "Selected publications and preprints.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/publications/";
          },
        },{id: "nav-projects",
          title: "projects",
          description: "Selected research and side projects in AI and systems.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/projects/";
          },
        },{id: "nav-cv",
          title: "cv",
          description: "Education, research experience, and skills.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/cv/";
          },
        },{id: "post-视频生成-infra-瓶颈与取舍",
        
          title: "视频生成 infra：瓶颈与取舍",
        
        description: "LLM serving 的直觉在视频生成上逐条失效：合批、加速、质量与流式服务。",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/video-gen-infra/";
          
        },
      },{id: "post-video-generation-infra-bottlenecks-and-trade-offs",
        
          title: "Video generation infra: bottlenecks and trade-offs",
        
        description: "LLM-serving intuitions fail one by one on video generation — batching, acceleration, quality and streaming.",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/video-gen-infra-en/";
          
        },
      },{id: "news-graduate-from-peking-university",
          title: 'Graduate from Peking University',
          description: "",
          section: "News",},{id: "news-joined-uiuc-and-started-m-s-program-advised-by-prof-fan-lai",
          title: 'Joined UIUC and started M.S. program, advised by Prof. Fan Lai',
          description: "",
          section: "News",},{id: "news-jitserve-has-been-accepted-to-nsdi-26",
          title: 'JITServe has been accepted to NSDI’26',
          description: "",
          section: "News",},{id: "news-joined-cisco-as-a-research-intern",
          title: 'Joined Cisco as a Research Intern',
          description: "",
          section: "News",},{id: "projects-iosd-improved-open-vocabulary-segmentation-with-diffusion-models",
          title: 'IOSD: Improved Open-vocabulary Segmentation with Diffusion Models',
          description: "Enhanced Grounded Diffusion for open-vocabulary segmentation using Stable Diffusion XL.",
          section: "Projects",handler: () => {
              window.location.href = "/projects/1_project/";
            },},{
        id: 'social-email',
        title: 'email',
        section: 'Socials',
        handler: () => {
          window.open("mailto:%7A%68%61%6E%67%77%32@%69%6C%6C%69%6E%6F%69%73.%65%64%75", "_blank");
        },
      },{
        id: 'social-github',
        title: 'GitHub',
        section: 'Socials',
        handler: () => {
          window.open("https://github.com/En-2863", "_blank");
        },
      },{
        id: 'social-linkedin',
        title: 'LinkedIn',
        section: 'Socials',
        handler: () => {
          window.open("https://www.linkedin.com/in/wei-zhang-0962372ba", "_blank");
        },
      },{
        id: 'social-scholar',
        title: 'Google Scholar',
        section: 'Socials',
        handler: () => {
          window.open("https://scholar.google.com/citations?user=mvn56BIAAAAJ", "_blank");
        },
      },{
      id: 'light-theme',
      title: 'Change theme to light',
      description: 'Change the theme of the site to Light',
      section: 'Theme',
      handler: () => {
        setThemeSetting("light");
      },
    },
    {
      id: 'dark-theme',
      title: 'Change theme to dark',
      description: 'Change the theme of the site to Dark',
      section: 'Theme',
      handler: () => {
        setThemeSetting("dark");
      },
    },
    {
      id: 'system-theme',
      title: 'Use system default theme',
      description: 'Change the theme of the site to System Default',
      section: 'Theme',
      handler: () => {
        setThemeSetting("system");
      },
    },];
