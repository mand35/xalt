#include <string.h>
#include "xalt_utils.h"
#include "xalt_config.h"

bool path2module(std::string& path, Table& rmapT, std::string& result)
{
  std::string p = path;

  while(1)
    {
      p.erase(p.rfind('/'), std::string::npos);
      if (rmapT.count(p) > 0)
        {
          result = rmapT[p];
          return true;
        }
    }
  return false;
}

FILE* xalt_file_open(const char* name)
{
  static const char *extA[]       = {".json", ".old.json"};
  static int         nExt         = sizeof(extA)/sizeof(extA[0]);
  const char*        xalt_etc_dir = getenv("XALT_ETC_DIR");
  std::string        fn;

  if (xalt_etc_dir == NULL)
    xalt_etc_dir = XALT_ETC_DIR;

  FILE*       fp    = NULL;
  const char* start = xalt_etc_dir;
  bool        done  = false;
  while(!done)
    {
      char * p = strchr((char *) start,':');
      if (p)
        fn.assign(start, p - start);  
      else
        {
          fn.assign(start);
          done = true;
        }

      for (int i = 0; i < nExt; ++i)
        {
          fn += "/";
          fn += name;
          fn += extA[i];
          fp  = fopen(fn.c_str(), "r");
          if (fp)
            break;
        }
      start = ++p;
    } 
  return fp;
}
