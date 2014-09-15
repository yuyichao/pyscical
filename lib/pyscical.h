#ifndef __PYSCICAL_PYSCICAL_H
#define __PYSCICAL_PYSCICAL_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#include "api.h"

#ifdef __cplusplus
}
#endif

#define PYSCICAL_EXPORT __attribute__((visibility("default")))
#define PYSCICAL_INLINE __attribute__((always_inline)) inline

#endif
