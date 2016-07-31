#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <unistd.h>
#include <stdlib.h>

#define BLOCK_SIZE 4096

typedef struct
{
	char *data;
	size_t alloc_size;
	size_t size;
}
string;

string empty_string()
{
	string ret;
	ret.data = NULL;
	ret.alloc_size = 0;
	ret.size = 0;
	return ret;
}

void append_char(string *str, char ch)
{
	if(str->size + 1 > str->alloc_size)
	{
		str->alloc_size += BLOCK_SIZE;
		str->data = realloc(str->data, str->alloc_size);
	}
	str->data[str->size++] = ch;
}

void append_read(string *str)
{
	str->alloc_size = str->size + BLOCK_SIZE;
	str->data = realloc(str->data, str->alloc_size);
	size_t sz = read(fileno(stdin), str->data + str->size, BLOCK_SIZE);
	if(sz == -1)
	{
		perror("read");
		exit(EXIT_FAILURE);
	}
	str->size += sz;
}

void destroy_string(string *str)
{
	free(str->data);
	str->data = NULL;
	str->alloc_size = 0;
	str->size = 0;
}

void write_all(string *str)
{
	size_t offset = 0;
	while(offset < str->size)
	{
		size_t sz = write(fileno(stdout), str->data + offset, str->size - offset);
		if(sz == -1)
		{
			perror("read");
			exit(EXIT_FAILURE);
		}
		offset += sz;
	}
}

int try_append_read(string *str, size_t offset)
{
	if(offset < str->size)
		return 1;
	append_read(str);
	if(offset < str->size)
		return 1;
	else
		return 0;
}

typedef struct
{
	signed char fg, bg;
	char bold:1;
	char underline:1;
}
state;

state default_state()
{
	state ret;
	ret.fg = ret.bg = -1;
	ret.bold = ret.underline = 0;
	return ret;
}

#define DIGIT(X) ('0' + (X))
#define UNDIGIT(X) ((X) - '0')
#define DIGIT1(N) DIGIT((N) / 10)
#define DIGIT2(N) DIGIT((N) % 10)

void emit_diff(string *str, state old, state new)
{
	if(old.fg != new.fg || old.bg != new.bg)
	{
		if(new.fg == -1)
		{
			if(new.bg == -1)
			{
				append_char(str, '\x03');
			}
			else
			{
				append_char(str, '\x16');
				append_char(str, '\x03');
				append_char(str, DIGIT1(new.bg));
				append_char(str, DIGIT2(new.bg));
				append_char(str, '\x16');
			}
		}
		else
		{
			if(new.bg == -1)
			{
				append_char(str, '\x03');
				append_char(str, '\x03');
				append_char(str, DIGIT1(new.fg));
				append_char(str, DIGIT2(new.fg));
			}
			else
			{
				append_char(str, '\x03');
				append_char(str, DIGIT1(new.fg));
				append_char(str, DIGIT2(new.fg));
				append_char(str, ',');
				append_char(str, DIGIT1(new.bg));
				append_char(str, DIGIT2(new.bg));
			}
		}
	}
	if(old.bold != new.bold)
		append_char(str, '\x02');
	if(old.underline != new.underline)
		append_char(str, '\x1F');
}

void dispatch(state *st, int code)
{
	switch(code)
	{
		case 0: *st = default_state(); break;
		case 1: st->bold = 1; break;
		case 4: st->underline = 1; break;
		case 22: st->bold = 0; break;
		case 24: st->underline = 0; break;

		case 30: st->fg = 1; break;
		case 31: st->fg = 4; break;
		case 32: st->fg = 3; break;
		case 33: st->fg = 7; break;
		case 34: st->fg = 2; break;
		case 35: st->fg = 6; break;
		case 36: st->fg = 10; break;
		case 37: st->fg = 15; break;

		case 39: st->fg = -1; break;

		case 40: st->bg = 1; break;
		case 41: st->bg = 4; break;
		case 42: st->bg = 3; break;
		case 43: st->bg = 7; break;
		case 44: st->bg = 2; break;
		case 45: st->bg = 6; break;
		case 46: st->bg = 10; break;
		case 47: st->bg = 15; break;

		case 49: st->fg = -1; break;

		case 90: st->fg = 14; break;
		case 91: st->fg = 4; break;
		case 92: st->fg = 9; break;
		case 93: st->fg = 8; break;
		case 94: st->fg = 12; break;
		case 95: st->fg = 13; break;
		case 96: st->fg = 11; break;
		case 97: st->fg = 0; break;

		case 100: st->bg = 14; break;
		case 101: st->bg = 4; break;
		case 102: st->bg = 9; break;
		case 103: st->bg = 8; break;
		case 104: st->bg = 12; break;
		case 105: st->bg = 13; break;
		case 106: st->bg = 11; break;
		case 107: st->bg = 0; break;
	}
}

int main(int argc, char *argv[])
{
	int keep_ansi = 1;
	if(argc > 1 && !strcmp(argv[1], "--remove"))
		keep_ansi = 0;
	state current = default_state();
	int needs_reemit = 0;
	do
	{
		string input = empty_string();
		append_read(&input);
		if(!input.size)
			break;
		string output = empty_string();
		size_t i = 0;
		for(i = 0; i < input.size; i++)
		{
			char ch = input.data[i];
			if(ch == '\x1B')
			{
				state old = current;
				if(!try_append_read(&input, i))
					break;
				if(input.data[i + 1] == '[')
				{
					size_t j;
					if(!try_append_read(&input, i + 2))
						break;
					int code = 0;
					for(j = i + 2; isdigit(input.data[j]) || input.data[j] == ';'; j++)
					{
						if(!try_append_read(&input, j + 1))
							break;
						if(input.data[j] == ';')
						{
							dispatch(&current, code);
							code = 0;
						}
						else if(isdigit(input.data[j]))
						{
							code = code * 10 + UNDIGIT(input.data[j]);
						}
					}
					if(isdigit(input.data[j]) || input.data[j] == ';')
						break;
					dispatch(&current, code);
					if(input.data[j] != 'm')
						current = old;
					emit_diff(&output, old, current);
					if(keep_ansi)
					{
						for(; i < j; i++)
							append_char(&output, input.data[i]);
						append_char(&output, input.data[i]);
					}
					else
					{
						i = j;
					}
					needs_reemit = 0;
					continue;
				}
			}
			if(ch == '\n' || ch == '\r')
			{
				needs_reemit = 1;
			}
			else if(needs_reemit)
			{
				emit_diff(&output, default_state(), current);
				needs_reemit = 0;
			}
			append_char(&output, ch);
		}
		write_all(&output);
	}
	while(1);
}
