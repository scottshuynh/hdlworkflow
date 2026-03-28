--------------------------------------------------------------------------------
-- Very basic checks on writing and reading from FIFO
-------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.standard_pkg.all;
use work.array_pkg.all;
use std.env.finish;

-----------------------------------------------------------

entity fifo_sync_tb is
  generic (
    DATA_W : natural := 16;
    DEPTH  : natural := 1024
  );
end entity fifo_sync_tb;

-----------------------------------------------------------

architecture testbench of fifo_sync_tb is

  -- Testbench DUT ports
  signal clk_i          : std_logic;
  signal rst_i          : std_logic;
  signal wr_en_i        : std_logic                             := '0';
  signal wr_data_i      : std_logic_vector(DATA_W - 1 downto 0) := (others => '0');
  signal rd_en_i        : std_logic                             := '0';
  signal rd_data_o      : std_logic_vector(DATA_W - 1 downto 0);
  signal rd_data_vld_o  : std_logic;
  signal full_o         : std_logic;
  signal empty_o        : std_logic;
  signal fill_counter_o : unsigned(ceil_log2(DEPTH) downto 0);

  constant NUM_WRITES : natural                                           := 10;
  signal wr_count     : unsigned(ceil_log2(DEPTH) downto 0)               := (others => '0');
  signal wr_values    : array_slv_t(0 to NUM_WRITES-1)(DATA_W-1 downto 0) := (others => (others => '0'));
  signal rd_count     : unsigned(ceil_log2(DEPTH) downto 0)               := (others => '0');
  signal rd_idx       : unsigned(ceil_log2(DEPTH) downto 0)               := (others => '0');

  -- Other constants
  constant C_CLK_PERIOD : real := 1.0e-9; -- NS

begin
  g_clk : process
  begin
    clk_i <= '1';
    wait for C_CLK_PERIOD / 2.0 * (1 SEC);
    clk_i <= '0';
    wait for C_CLK_PERIOD / 2.0 * (1 SEC);
  end process;

  g_rst : process
  begin
    rst_i <= '1',
      '0' after 20.0*C_CLK_PERIOD * (1 SEC);
    wait;
  end process;

  DUT : entity work.fifo_sync
    generic map (
      DATA_W => DATA_W,
      DEPTH  => DEPTH
    )
    port map (
      clk_i          => clk_i,
      rst_i          => rst_i,
      wr_en_i        => wr_en_i,
      wr_data_i      => wr_data_i,
      rd_en_i        => rd_en_i,
      rd_data_o      => rd_data_o,
      rd_data_vld_o  => rd_data_vld_o,
      full_o         => full_o,
      empty_o        => empty_o,
      fill_counter_o => fill_counter_o
    );

  p_clk : process (clk_i)
  begin
    if rising_edge(clk_i) then
      wr_en_i <= '0';
      rd_en_i <= '0';
      if (wr_count < NUM_WRITES) then
        wr_en_i                         <= '1';
        wr_count                        <= wr_count + 1;
        wr_data_i                       <= std_logic_vector(resize(wr_count + 1, DATA_W));
        wr_values(to_integer(wr_count)) <= std_logic_vector(resize(wr_count + 1, DATA_W));
      end if;

      if (wr_count > 2 and rd_count < NUM_WRITES) then
        rd_en_i  <= '1';
        rd_count <= rd_count + 1;
      end if;

      if (rd_data_vld_o = '1') then
        assert rd_data_o = (wr_values(to_integer(rd_idx)));
        rd_idx <= rd_idx + 1;
      end if;

      if (rd_idx >= NUM_WRITES) then
        finish;
      end if;

      if (rst_i = '1') then
        wr_en_i   <= '0';
        rd_en_i   <= '0';
        wr_count  <= (others => '0');
        wr_data_i <= (others => '0');
        wr_values <= (others => (others => '0'));
        rd_count  <= (others => '0');
        rd_idx    <= (others => '0');
      end if;
    end if;
  end process;

end architecture;