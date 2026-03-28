--------------------------------------------------------------------------------
-- Synchronous FIFO, 1 clock cycle latency.
--------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.standard_pkg.all;

entity fifo_sync is
  generic (
    DATA_W : natural;
    DEPTH  : natural
  );
  port (
    clk_i          : in std_logic;
    rst_i          : in std_logic;
    wr_en_i        : in std_logic;
    wr_data_i      : in std_logic_vector(DATA_W - 1 downto 0);
    rd_en_i        : in std_logic;
    rd_data_o      : out std_logic_vector(DATA_W - 1 downto 0);
    rd_data_vld_o  : out std_logic;
    full_o         : out std_logic;
    empty_o        : out std_logic;
    fill_counter_o : out unsigned(ceil_log2(DEPTH) downto 0)
  );
end entity fifo_sync;

architecture rtl of fifo_sync is

  constant ADDR_W : natural := ceil_log2(DEPTH);
  signal empty    : std_logic;
  signal full     : std_logic;

  signal wr_en   : std_logic;
  signal wr_addr : unsigned(ADDR_W - 1 downto 0) := (others => '0');

  signal rd_en        : std_logic;
  signal rd_addr      : unsigned(ADDR_W - 1 downto 0) := (others => '0');
  signal fill_counter : unsigned(ADDR_W downto 0)     := (others => '0');

begin

  i_ram_simple_dual_port : entity work.ram_simple_dual_port
    generic map(
      DATA_W       => DATA_W,
      ADDR_W       => ceil_log2(DEPTH),
      BYTE_W       => DATA_W,
      NUM_PIPELINE => 0
    )
    port map
    (
      clk_i         => clk_i,
      wr_ce_i       => '1',
      wr_en_i(0)    => wr_en,
      wr_addr_i     => wr_addr,
      wr_data_i     => wr_data_i,
      rd_ce_i       => rd_en,
      rd_addr_i     => rd_addr,
      rd_data_o     => rd_data_o,
      rd_data_vld_o => rd_data_vld_o
    );

  process (all)
  begin
    if wr_addr = rd_addr and fill_counter = 0 then
      empty <= '1';
    else
      empty <= '0';
    end if;
    empty_o <= empty;

    if fill_counter(fill_counter'high) = '1' then
      full <= '1';
    else
      full <= '0';
    end if;
    full_o <= full;

    if wr_en_i = '1' and full = '0' then
      wr_en <= '1';
    else
      wr_en <= '0';
    end if;

    if rd_en_i = '1' and empty = '0' then
      rd_en <= '1';
    else
      rd_en <= '0';
    end if;
  end process;

  process (clk_i)
  begin
    if rising_edge(clk_i) then
      if wr_en_i = '1' then
        if full = '0' then
          wr_addr      <= wr_addr + 1;
          fill_counter <= fill_counter + 1;
        end if;
      end if;

      if rd_en_i = '1' then
        if empty = '0' then
          rd_addr      <= rd_addr + 1;
          fill_counter <= fill_counter - 1;
        end if;
      end if;

      if rd_en_i = '1' and wr_en_i = '1' then
        if empty = '0' then
          fill_counter <= fill_counter;
        end if;
      end if;

      if rst_i = '1' then
        wr_addr      <= (others => '0');
        rd_addr      <= (others => '0');
        fill_counter <= (others => '0');
      end if;

    end if;
  end process;

  fill_counter_o <= fill_counter;

end architecture;
