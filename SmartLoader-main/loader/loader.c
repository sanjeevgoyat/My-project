#include "loader.h"
#define page_size 4096

Elf32_Ehdr *ehdr;
Elf32_Phdr *phdr;
int fd;
void *a;
int no_page_fault = 0;
int total_mem_allocated = 0;
int total_mem_used = 0;
int no_page_allocation = 0;

typedef struct MemoryNode {
    void *address;
    size_t size;
    struct MemoryNode *next;
} MemoryNode;

MemoryNode *head = NULL;

void add_memory_allocation(void *address, size_t size) {
    MemoryNode *new_node = (MemoryNode *)malloc(sizeof(MemoryNode));
    if (new_node == NULL) {
        perror("Error allocating memory for linked list node");
        return;
    }
    new_node->address = address;
    new_node->size = size;
    new_node->next = head;
    head = new_node;
}

void free_all_allocations() {
    MemoryNode *current = head;
    while (current != NULL) {
        munmap(current->address, current->size);
        MemoryNode *temp = current;
        current = current->next;
        free(temp);
    }
    head = NULL;
}

void segfault_handler(int signo, siginfo_t *info, void *context)
{
  no_page_fault++;
  printf("Segmentation fault occurred. Address: %p\n", info->si_addr);
  Elf32_Phdr *entry_phdr = NULL;
  int i = 0;

  while (i < ehdr->e_phnum)
  {
    if ((void *)info->si_addr >= (void *)phdr[i].p_vaddr && (void *)info->si_addr < (void *)(phdr[i].p_vaddr + phdr[i].p_memsz))
    {
      entry_phdr = &phdr[i];
      float no_pages = (float)(entry_phdr->p_memsz) / (float)(page_size);

      if (no_pages > (int)no_pages)
      {
        no_pages = (int)no_pages + 1;
      }
      else
      {
        no_pages = (int)no_pages;
      }
      int mem_size = no_pages * page_size;
      total_mem_allocated += mem_size;
      total_mem_used += entry_phdr->p_memsz;
      no_page_allocation += no_pages;
      printf("%d mem size\n", mem_size);
      printf("%d actual size\n", entry_phdr->p_memsz);
      void *virtual_mem = mmap((void *)entry_phdr->p_vaddr, mem_size, PROT_READ | PROT_WRITE | PROT_EXEC, MAP_ANONYMOUS | MAP_PRIVATE, 0, 0);
      if (virtual_mem == MAP_FAILED)
      {
        perror("Error in memory mapping through mmap");
        break;
      }
      add_memory_allocation(virtual_mem, mem_size);
      memcpy(virtual_mem, (void *)((char *)a + entry_phdr->p_offset), mem_size);
      virtual_mem = (char *)(virtual_mem);
      break;
    }
    i++;
  }

  if (entry_phdr == NULL)
  {
    perror("Entry point not found in any phdr.");
    return;
  }
}

void loader_cleanup()
{
  free_all_allocations(); 
  if (fd != -1)
  {
    close(fd);
    return;
  }
}

int size_of_file;
int file_reader()
{
  ssize_t read_the_file = read(fd, a, size_of_file); // read_the_file is equal to the number of bytes read in file
  if (read_the_file != size_of_file)
  {
    close(fd);
    return 0;
  }
  return 1;
};

void load_and_run_elf(const char *exe)
{
  fd = open(exe, O_RDONLY);
  if (fd == -1) // to check whether file descriptor is opened
  {
    perror("Error in opening elf file with file descriptor");
    close(fd);
    return;
  }

  size_of_file = lseek(fd, 0, SEEK_END); // to get the size of the file descriptor (fd)
  lseek(fd, 0, SEEK_SET);

  if (size_of_file == -1)
  {
    perror("Error getting the file size");
    close(fd);
    return;
  }

  if (file_reader == 0)
  {
    perror("Error in reading file");
    close(fd);
    return;
  }

  // 1. Load entire binary content into the memory from the ELF file.

  a = (void *)malloc(size_of_file); // allocates dynamic memory on heap equal to the size of fd
  if (a == NULL)
  {
    perror("Error in allocating memory on heap");
    close(fd);
    return;
  }

  ehdr = (Elf32_Ehdr *)a;                           // typecasting contents of "a" into Elf32_Ehdr one.
  phdr = (Elf32_Phdr *)((char *)a + ehdr->e_phoff); // e_phoff is Program header offset

  struct sigaction sa;
  sa.sa_flags = SA_SIGINFO;
  sa.sa_sigaction = segfault_handler;

  // 2. Iterate through the PHDR table and find the section of PT_LOAD
  char *entry_point_in_segment = NULL;
  int i = 0;
  close(fd);
  free(a);

  if (sigaction(SIGSEGV, &sa, NULL) == -1)
  {
    perror("Error setting up SIGSEGV handler");
    return;
  }

  int (*_start)() = (int (*)())(intptr_t)ehdr->e_entry;

  int result = _start();
  printf("User _start return value = %d\n", result);
  printf("No of page faults: %d\n", no_page_fault);
  printf("Total memory allocated: %d\n", total_mem_allocated);
  printf("Total memmory used: %d\n", total_mem_used);
  printf("Internal fragmentation: %.2f KB\n", (float)(total_mem_allocated - total_mem_used) / 1024);
  printf("Total page allocation: %d\n", no_page_allocation);
}
