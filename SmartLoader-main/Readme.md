# Assignment Details
In Assignment-1, the implementation of Simple Loader, we used to load any program segments upfront, but in this code we do not do the same we only load the segment only
when needed while the program is under execution (i.e., lazily – as it happens in case of Linux as well). Its working is really simple and is explained below.
SimpleSmartLoader will also work only for ELF 32-bit executable without having any references to glibc APIs.

## Assignment Working
1. The SimpleSmartLoader will directly attempt running the _start method by typecasting the entrypoint address. However, doing so will generate a segmentation fault as 
that memory page does not exist.
2. Segmentation faults are generated for invalid memory accesses, but in this assignment, segmentation faults are happening due to accessing unallocated segments. As 
the address generating the segmentation fault is valid, this segmentation fault can be treated as a page fault because the physical page allocation hasn’t happened for 
that segment address.
3. SimpleSmartLoader should handle such segmentation faults by allocating memory using mmap and then load the appropriate segments (i.e., loading and copying is carried 
out lazily). Total memory allocated by mmap must be multiple of page size (4KB).
4. SimpleSmartLoader should be able to dynamically mmap memory and copy the complete content of a segment during the program execution (in one-shot) without terminating 
the program. The program should simply resume after the segmentation fault is handled appropriately.
5. After the execution of the executable, SimpleSmartLoader will report: (i) the total number of page faults and (ii) total number of page 
allocations carried out for 
that executable’s execution, (iii) total amount of internal fragmentation in KB.

## implementation
When segfault is occured, we called handler which checks and find for which segment the faulting address is present. Then, we allocate a 
page for that segment using 
mmap and then lseek through file descriptor to find the correct segment in fd anf then read it into allocated memory. We calculated page 
fault asssuming that total no 
of seg fault is equal to page faults and total number of pages and internal fragmentation for each required segment ( one time only ) by 
keeping check if it has previously arrived or not.

# Contribution 
1. Satvik Arya(2023493) :- correcting typecasting, find address where segmentation fault( page fault) is occuring and identifying the 
segment where faulting address is present.
2. Sanjeev(2023483) :- allocating correct memory segment using mmap, read and lseek and calculating number of page fault, number of page 
allocated and total internal fragmentation.

## Github Link
https://github.com/Satvik1924/SmartLoader

