/*
 * Copyright (c) 2013 Juniper Networks, Inc. All rights reserved.
 */

#ifndef __VIZD_TABLE_DESC_H__
#define __VIZD_TABLE_DESC_H__

#include <boost/tuple/tuple.hpp>
#include <analytics/viz_types.h>
#include "database/gendb_if.h"

extern std::vector<GenDb::NewCf> vizd_tables;
extern std::vector<GenDb::NewCf> vizd_stat_tables;
extern std::vector<GenDb::NewCf> vizd_session_tables;

typedef boost::tuple<SessionRecordFields::type, GenDb::DbDataType::type> SessionTypeInfo;
typedef std::map<std::string, SessionTypeInfo> SessionTypeMap;
extern SessionTypeMap session_msg2type_map;

void init_vizd_tables(void);

#endif // __VIZD_TABLE_DESC_H__
