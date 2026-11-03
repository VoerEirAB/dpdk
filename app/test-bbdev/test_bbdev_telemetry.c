/* SPDX-License-Identifier: BSD-3-Clause
 * Copyright(c) 2024 VoerEir AB
 */

#include <errno.h>
#include <stdlib.h>
#include <string.h>

#include <rte_common.h>
#include <stdio.h>
#include <rte_bbdev.h>
#include <rte_telemetry.h>

static int
handle_bbdev_list(const char *cmd __rte_unused,
		const char *params __rte_unused, struct rte_tel_data *d)
{
	uint16_t dev_id;

	rte_tel_data_start_array(d, RTE_TEL_INT_VAL);
	for (dev_id = 0; dev_id < RTE_BBDEV_MAX_DEVS; dev_id++)
		if (rte_bbdev_is_valid(dev_id))
			rte_tel_data_add_array_int(d, dev_id);
	return 0;
}

static int
handle_bbdev_stats(const char *cmd __rte_unused, const char *params,
		struct rte_tel_data *d)
{
	struct rte_bbdev_stats stats;
	struct rte_tel_data *status;
	char *end;
	unsigned long dev_id;
	unsigned int i;
	char name[32];

	if (params == NULL || params[0] == '\0')
		return -EINVAL;
	errno = 0;
if (params[0] < '0' || params[0] > '9')
		return -EINVAL;
	dev_id = strtoul(params, &end, 10);
	if (errno != 0 || *end != '\0' || dev_id >= RTE_BBDEV_MAX_DEVS)
		return -EINVAL;
	if (!rte_bbdev_is_valid(dev_id))
		return -EINVAL;
	if (rte_bbdev_stats_get(dev_id, &stats) != 0)
		return -EINVAL;

	rte_tel_data_start_dict(d);
	rte_tel_data_add_dict_uint(d, "enqueued_count", stats.enqueued_count);
	rte_tel_data_add_dict_uint(d, "dequeued_count", stats.dequeued_count);
	rte_tel_data_add_dict_uint(d, "enqueue_err_count",
			stats.enqueue_err_count);
	rte_tel_data_add_dict_uint(d, "dequeue_err_count",
			stats.dequeue_err_count);
	rte_tel_data_add_dict_uint(d, "enqueue_warn_count",
			stats.enqueue_warn_count);
	rte_tel_data_add_dict_uint(d, "dequeue_warn_count",
			stats.dequeue_warn_count);
	rte_tel_data_add_dict_uint(d, "acc_offload_cycles",
			stats.acc_offload_cycles);
	rte_tel_data_add_dict_uint(d, "enqueue_depth_avail",
			stats.enqueue_depth_avail);

	status = rte_tel_data_alloc();
	if (status == NULL)
		return -ENOMEM;
	rte_tel_data_start_dict(status);
	for (i = 0; i < RTE_BBDEV_ENQ_STATUS_SIZE_MAX; i++) {
		snprintf(name, sizeof(name), "status_%u", i);
		rte_tel_data_add_dict_uint(status, name,
				stats.enqueue_status_count[i]);
	}
	rte_tel_data_add_dict_container(d, "enqueue_status_count", status, 0);
	return 0;
}

RTE_INIT(test_bbdev_telemetry_init)
{
	rte_telemetry_register_cmd("/bbdev/list", handle_bbdev_list,
		"Returns list of bbdev device ids. Takes no parameters");
	rte_telemetry_register_cmd("/bbdev/stats", handle_bbdev_stats,
		"Returns stats of a bbdev device. Parameters: int device_id");
}
