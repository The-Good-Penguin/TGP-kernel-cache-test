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
#include <linux/efi-bootcache.h>
static int __init bootcache_test_init(void)
{
	pr_info("bootcache-test module loading\n");
	
	/* Test for bootcache variables! */
	
	u32 vardata;
	int res;
	
	res = bootcache_get_u32(NULL, "testvar1", &vardata);
	if (res)
	    pr_info("res for test testvar1 = %d\n", res);
	else
    	pr_info("testvar1 = 0x%x\n", vardata);

	pr_info("Testing how to create a variable\n");

	res = bootcache_set_u32(NULL, "testvar2", 0xDEADBEEF);
	pr_info("  res for testvar2 creation = %d\n", res);

	res = bootcache_set_u32(NULL, "testvar3", 0xABADCAFE);
	pr_info("  res for testvar3 creation = %d\n", res);

	pr_info("Testing changing a variable\n");
	res = bootcache_set_u32(NULL, "testvar1", 0x55AA55AA);
	pr_info("  res for testvar1 change = %d\n", res);

	
	pr_info("Testing the values read back\n");
	res = bootcache_get_u32(NULL, "testvar1", &vardata);
	pr_info("  testvar1 = 0x%x\n", vardata);

	res = bootcache_get_u32(NULL, "testvar2", &vardata);
	pr_info("  testvar2 = 0x%x\n", vardata);

	res = bootcache_get_u32(NULL, "testvar3", &vardata);
	pr_info("  testvar3 = 0x%x\n", vardata);

	/* Debugging dump */
	pr_info("Dumping debugging information out\n");
	bootcache_dbg();


	pr_info("Incremeting testCounter\n");
	if (res = bootcache_get_u32(NULL, "testCounter", &vardata)) { 
	  res = bootcache_set_u32(NULL, "testCounter", 0x0);
	}
	else {
	  pr_info("  Current testCounter = %d\n", vardata);
	  pr_info("  Incrementing..\n", vardata);
	  res = bootcache_set_u32(NULL, "testCounter", vardata+1);
	}
	pr_info("  res for testCounter change = %d\n", res);
	
	return 0;
}

static void __exit bootcache_test_exit(void)
{
	pr_info("bootcache-test module unloading\n");

	pr_info("Triggering an update of saved variables\n");
	bootcache_writeout();
	bootcache_dbg();
}

module_init(bootcache_test_init);
module_exit(bootcache_test_exit);
MODULE_LICENSE("GPL");
