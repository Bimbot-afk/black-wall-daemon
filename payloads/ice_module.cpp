#include <emscripten/em_macros.h>
#include <emscripten/emscripten.h>
#include <iostream>

extern "C" {
EMSCRIPTEN_KEEPALIVE
void deploy_defense() {
  std::cout << "Net watcher on." << std::endl;

  EM_ASM(document.body.style.backgroundColor = "red";
         alert("Defense deployed."));
}
}