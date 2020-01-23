#!/bin/bash
echo " --------------"
echo " Unpacking tarball ..."
tar -xf gc_tarball.tar.gz
echo " Sucessfully unpacked tarball"
echo " --------------"
echo " Starting shape Production ! "
bash ./shapes/produce_shapes_remote.sh
echo " Finished shape Production ! "
echo " --------------"
# echo " Packing result tarball ..."
# tar -czf gc_output.tar.gz output