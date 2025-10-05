import React, { useState } from "react";
import { BarChart, Rocket, Menu, X } from "lucide-react";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  const navItems = [
    { name: "Data", icon: BarChart },
    { name: "Mission", icon: Rocket },
  ];

  const handleNavClick = (e, item) => {
    if (item.name === "Mission") {
      e.preventDefault();
      const el = document.getElementById("mision");
      if (el) {
        const headerOffset = 64; 
        const elementPosition =
          el.getBoundingClientRect().top + window.pageYOffset;
        const offsetPosition = elementPosition - headerOffset;
        window.scrollTo({ top: offsetPosition, behavior: "smooth" });
        setIsOpen(false);
      } else {
        window.location.hash = "mision";
      }
    } else if (item.name === "Data") {
      e.preventDefault();
      const el = document.getElementById("data");
      if (el) {
        const headerOffset = 64; 
        const elementPosition =
          el.getBoundingClientRect().top + window.pageYOffset;
        const offsetPosition = elementPosition - headerOffset;
        window.scrollTo({ top: offsetPosition, behavior: "smooth" });
        setIsOpen(false);
      } else {
        window.location.hash = "data";
      }
    }
  };

  return (
    <nav className="fixed top-0 left-0 w-full z-50 bg-gray-900/80 backdrop-blur-md shadow-lg border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <a href="#">
                <span className="text-2xl font-bold text-white tracking-wider">
                  Cloud<span className="text-cyan-400">Busters</span>
                </span>
              </a>
            </div>
          </div>

          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-4">
              {navItems.map((item) => (
                <a
                  key={item.name}
                  href={item.name === "Misión" ? "#mision" : "#"}
                  onClick={(e) => handleNavClick(e, item)}
                  className="px-3 py-2 rounded-md text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white transition duration-200 flex items-center"
                >
                  <item.icon className="w-4 h-4 mr-1" />
                  {item.name}
                </a>
              ))}
            </div>
          </div>

          <div className="md:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="bg-gray-800 p-2 rounded-md inline-flex items-center justify-center text-gray-400 hover:text-white hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-cyan-500"
            >
              {isOpen ? (
                <X className="block h-6 w-6" aria-hidden="true" />
              ) : (
                <Menu className="block h-6 w-6" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>
      </div>

      {isOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 border-t border-gray-800">
            {navItems.map((item) => (
              <a
                key={item.name}
                href={item.name === "Misión" ? "#mision" : "#"}
                onClick={(e) => handleNavClick(e, item)}
                className="block px-3 py-2 rounded-md text-base font-medium text-gray-300 hover:bg-gray-700 hover:text-white transition duration-200 flex items-center"
              >
                <item.icon className="w-4 h-4 mr-2" />
                {item.name}
              </a>
            ))}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
