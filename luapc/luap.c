#include <stdlib.h>
#include <stdio.h>
#include <lua.h>
#include <lualib.h>
#include <lauxlib.h>

const unsigned int maxmem = 2000000;

static void* luap_allocateMemory(void *ud, void *ptr, size_t osize, size_t nsize) {
    long delta = nsize - osize;
    if (nsize == 0) {
        free(ptr);
        *(unsigned int*)ud += delta;
        return NULL;
    }
    else {
        if (*(unsigned int*)ud + delta < maxmem) {
            *(unsigned int*)ud += delta;
            return realloc(ptr, nsize);
        }
        else {
            return NULL;
        }
    }
}

static void luap_errout(int errnum) {
    if (errnum == LUA_OK) {return;}
    char *err;
    switch (errnum) {
        case(LUA_ERRRUN):
            err = "RuntimeError";
            break;
        case(LUA_ERRMEM):
            err = "MemoryError";
            break;
        case(LUA_ERRERR):
            err = "MessagehandlerError";
            break;
        case(LUA_ERRSYNTAX):
            err = "SyntaxError";
            break;
        case(LUA_YIELD):
            err = "YieldError";
            break;
        case(LUA_ERRFILE):
            err = "FileError";
            break;
        default:
            err = "UndefinedError";
            break;
    }

    fprintf(stderr, "%s\n", err);
}

int main() {
    char source[2020];
    unsigned int ud = 0;

    fread(source, sizeof(source), sizeof(source[0]), stdin);
    lua_State *L = lua_newstate(luap_allocateMemory, &ud);

    luaL_requiref(L, "math", luaopen_math, 1); // Adds math library
    luaL_requiref(L, "_G", luaopen_base, 1); // Adds base library

    /* This part removes some
     * unwanted functions from
     * the base library.       */
    lua_settop(L, 16);
    lua_setglobal(L, "collectgarbage");
    lua_setglobal(L, "dofile");
    lua_setglobal(L, "load");
    lua_setglobal(L, "loadfile");
    lua_setglobal(L, "require");
    lua_settop(L, 0); // Clears stack
    //luaL_dostring(L, source);
    luaL_loadstring(L, source);
    int status = lua_pcall(L, 0, LUA_MULTRET, 0);
    luap_errout(status);
    lua_close(L);
}

