/******************************************************************************
 *
 *   Copyright (C) 2011  Intel Corporation. All rights reserved.
 *
 *   This program is free software;  you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation; version 2 of the License.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY;  without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See
 *   the GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with this program;  if not, write to the Free Software
 *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
 *
 *****************************************************************************/

#include <linux/module.h>
#include <linux/bootcache.h>

#define DRIVER_NAME "bootcache_tester"

struct test_data {
	const char *name;
	u32 value;
};

static struct test_data test_data_array[] = {
	{
		.name = "Bootcache Test One",
		.value = 1234,
	},
	{
		.name = "Bootcache Test Two",
		.value = 5678,
	},
	{
		.name = "Bootcache Test Three",
		.value = 9012,
	},
	{
		.name = "Bootcache Test Four",
		.value = 0xDEADBEEF,
	},
	{
		.name = "Bootcache Test Five",
		.value = 0xC0DEBAD0,
	}
};

static int __init bootcache_test_init(void)
{
	pr_info("bootcache-test module loading\n");

	/* Test for bootcache variables! */

	u32 vardata;
	int res;
	int i;

	for (i = 0; i < ARRAY_SIZE(test_data_array); i++) {
		res = bootcache_get_u32(test_data_array[i].name, &vardata);
		if (res)
			pr_info("%s: res for %s = %d\n", DRIVER_NAME, test_data_array[i].name, res);
		else {
			pr_info("%s : %s = 0x%x\n", DRIVER_NAME, test_data_array[i].name, vardata);
			pr_info("%s : %s is %s\n",  DRIVER_NAME, test_data_array[i].name,
				(test_data_array[i].value == vardata) ? "Correct" : "Incorrect");
		}
	}

	/* Test writing variables and reading back */
	pr_info("Testing how to create a variable\n");

	res = bootcache_set_u32("testvar1", 0xDEADBEEF);
	pr_info("%s: res for testvar1 creation = %d\n", DRIVER_NAME, res);

	pr_info("Testing the values read back\n");
	res = bootcache_get_u32("testvar1", &vardata);
	pr_info("%s: testvar1 = 0x%x\n", DRIVER_NAME, vardata);

	pr_info("Testing changing a variable\n");
	res = bootcache_set_u32("testvar1", 0x55AA55AA);
	pr_info("%s: res for testvar1 change = %d\n", DRIVER_NAME, res);

	pr_info("Testing the values read back\n");
	res = bootcache_get_u32("testvar1", &vardata);
	pr_info("%s: testvar1 = 0x%x\n", DRIVER_NAME, vardata);

	pr_info("%s : Incremeting testCounter\n", DRIVER_NAME);
	res = bootcache_get_u32("testCounter", &vardata);
	if (res)
		res = bootcache_set_u32("testCounter", 0x1);
	else {
		pr_info("%s: Current testCounter = %d\n", DRIVER_NAME, vardata);
		pr_info("%s: Incrementing..\n", DRIVER_NAME);
		res = bootcache_set_u32("testCounter", vardata+1);
	}
	pr_info("%s : res for testCounter change = %d\n", DRIVER_NAME, res);

	return 0;
}

static void __exit bootcache_test_exit(void)
{
	pr_info("bootcache-test module unloading\n");

}

module_init(bootcache_test_init);
module_exit(bootcache_test_exit);
MODULE_LICENSE("GPL");
