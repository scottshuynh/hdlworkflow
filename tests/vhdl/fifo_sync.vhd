--------------------------------------------------------------------------------
-- Synchronous FIFO, 1 clock cycle latency.
--------------------------------------------------------------------------------

library ieee;
  use ieee.std_logic_1164.all;
  use ieee.numeric_std.all;

use work.standard_pkg.all;
use work.array_pkg.all;

entity fifo_sync is
  generic (
    DATA_W   : natural;
    DEPTH    : natural;
    IS_FWFT  : boolean := FALSE;
    NUM_PIPE : natural := 1
  );
  port (
    clk_i          : in    std_logic;
    rst_i          : in    std_logic;
    wr_en_i        : in    std_logic;
    wr_data_i      : in    std_logic_vector(DATA_W - 1 downto 0);
    rd_en_i        : in    std_logic;
    rd_data_o      : out   std_logic_vector(DATA_W - 1 downto 0);
    rd_data_vld_o  : out   std_logic;
    full_o         : out   std_logic;
    empty_o        : out   std_logic;
    fill_counter_o : out   unsigned(ceil_log2(DEPTH) downto 0)
  );
end entity fifo_sync;

architecture rtl of fifo_sync is
  constant ADDR_W     : natural := ceil_log2(DEPTH);
  signal   empty      : std_logic;
  signal   full       : std_logic;

  signal wr_en        : std_logic;
  signal wr_addr      : unsigned(ADDR_W - 1 downto 0) := (others => '0');

  signal rd_ce        : std_logic;
  signal rd_en        : std_logic;
  signal rd_addr      : unsigned(ADDR_W - 1 downto 0) := (others => '0');
  signal fill_counter : unsigned(ADDR_W downto 0)     := (others => '0');

  signal rd_data      : std_logic_vector(DATA_W - 1 downto 0) := (others => '0');
  signal rd_vld       : std_logic                             := '0';

begin

  i_ram_simple_dual_port : entity work.ram_simple_dual_port
    generic map (
      DATA_W       => DATA_W,
      ADDR_W       => ADDR_W,
      BYTE_W       => DATA_W,
      NUM_PIPELINE => NUM_PIPE
    )
    port map (
      clk_i         => clk_i,
      wr_ce_i       => '1',
      wr_en_i(0)    => wr_en,
      wr_addr_i     => wr_addr,
      wr_data_i     => wr_data_i,
      rd_ce_i       => rd_ce,
      rd_en_i       => rd_en,
      rd_addr_i     => rd_addr,
      rd_data_o     => rd_data,
      rd_data_vld_o => rd_vld
    );

  process (all) is
  begin
    if (fill_counter = 0) then
      empty <= '1';
    else
      empty <= '0';
    end if;

    if (fill_counter = DEPTH) then
      full <= '1';
    else
      full <= '0';
    end if;

    if (wr_en_i and not full) then
      wr_en <= '1';
    else
      wr_en <= '0';
    end if;
  end process;

  empty_o <= empty;
  full_o  <= full;

  process (clk_i) is
  begin
    if rising_edge(clk_i) then
      if (wr_en = '1') then
        wr_addr      <= wr_addr + 1;
        fill_counter <= fill_counter + 1;
      end if;

      if (rd_en and rd_ce) then
        rd_addr      <= rd_addr + 1;
        fill_counter <= fill_counter - 1;
      end if;

      if (rd_en and rd_ce and wr_en) then
        fill_counter <= fill_counter;
      end if;

      if (rst_i = '1') then
        wr_addr      <= (others => '0');
        rd_addr      <= (others => '0');
        fill_counter <= (others => '0');
      end if;
    end if;
  end process;

  g_fwft : if IS_FWFT generate
    signal rd_rdy : std_logic;
  begin

    process (all) is
    begin
      rd_ce <= rd_rdy;

      if (not empty) then
        rd_en <= '1';
      else
        rd_en <= '0';
      end if;
    end process;

    i_skid_buffer : entity work.skid_buffer
      generic map (
        DATA_W => DATA_W,
        DEPTH  => NUM_PIPE + 1
      )
      port map (
        clk_i      => clk_i,
        rst_i      => rst_i,
        src_data_i => rd_data,
        src_vld_i  => rd_vld,
        src_rdy_o  => rd_rdy,
        dst_data_o => rd_data_o,
        dst_vld_o  => rd_data_vld_o,
        dst_rdy_i  => rd_en_i
      );

  end generate g_fwft;

  g_std : if not IS_FWFT generate

    process (all) is
    begin
      rd_ce <= '1';

      if (rd_en_i and not empty) then
        rd_en <= '1';
      else
        rd_en <= '0';
      end if;
    end process;

    rd_data_o     <= rd_data;
    rd_data_vld_o <= rd_vld;

  end generate g_std;

  fill_counter_o <= fill_counter;

end architecture rtl;
